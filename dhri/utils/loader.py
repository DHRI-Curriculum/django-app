import requests, json
from pathlib import Path
from datetime import datetime, timedelta

from dhri.utils.markdown import split_into_sections
from dhri.constants import NORMALIZING_SECTIONS, BRANCH_AUTO, DOWNLOAD_CACHE_DIR, TEST_AGE, BACKEND_AUTO
from dhri.backend import *
from dhri.models import *
from dhri.logger import Logger
from dhri.utils.exceptions import UnresolvedNameOrBranch


log = Logger()

SECTIONS = {
    'frontmatter': {
        'abstract': Frontmatter,
        'learning_objectives': LearningObjective,
        'estimated_time': Frontmatter,
        'contributors': Contributor,
        'ethical_considerations': Frontmatter,
        'readings': Reading,
        'projects': Project,
    },
    'praxis': {
        'discussion_questions': Praxis,
        'next_steps': Praxis,
        'tutorials': Tutorial,
        'further_readings': Reading,
    },
    'assessment': {
        # TODO: add here
    }
}


def normalize_data(data, section):
    _ = {}
    for normalized_key, alts in NORMALIZING_SECTIONS[section].items():
        for alt in alts:
            done = False
            for key, val in data.items():
                if done:
                    continue
                if key.lower() == alt.lower():
                    _[normalized_key] = val
                    done = True
    return(_)




class Loader():
    """
    Downloads all the raw content from a provided repository on GitHub, and from a particular master.

    The repository must be *public* and must contain the following three files:
    - frontmatter.md
    - theory-to-practice.md
    - assessment.md
    """
    meta = {}
    content = {}

    _frontmatter_sections = SECTIONS['frontmatter']

    _praxis_sections = SECTIONS['praxis']
    
    frontmatter_models = {}
    for section, model in _frontmatter_sections.items():
        if not model in frontmatter_models: frontmatter_models[model] = []
        frontmatter_models[model].append(section)

    praxis_models = {}
    for section, model in _praxis_sections.items():
        if not model in praxis_models: praxis_models[model] = []
        praxis_models[model].append(section)

    
    def __init__(self, repo='https://www.github.com/kallewesterling/dhri-test-repo', branch=BRANCH_AUTO, download=True):
        self.repo = repo
        self.branch = branch
        self.download = download

        self._verify_repo()
        
        self.user = self.repo.split('/')[3]
        self.repo_name = self.repo.split('/')[4]
        
        self.name = self.repo_name.replace("-", " ").title()
        
        self.cache = LoaderCache(self.repo_name)
        
        # Set up raw urls
        self._raw_url = f'https://raw.githubusercontent.com/{self.user}/{self.repo_name}/{self.branch}'

        self.frontmatter_path = f'{self._raw_url}/frontmatter.md'
        self.praxis_path = f'{self._raw_url}/theory-to-practice.md'
        self.assessment_path = f'{self._raw_url}/assessment.md'

        if not self.cache.exists:
            if self.download:
                self._raw_content = self._get_raw_content()
                self.cache.save_cache(self.cache, self._raw_content)
        else:
            self._raw_content = self.cache.load_cache()

                
        self.meta = self._raw_content['meta']
        self.parent_backend = BACKEND_AUTO
        self.parent_repo = f"{self.user}/{self.repo_name}"
        self.parent_branch = self.branch

        self.content = self._raw_content['content']

        self._frontmatter_raw = self.content.get('frontmatter')
        self._praxis_raw = self.content.get('theory-to-practice')
        self._assessment_raw = self.content.get('assessment')

        self._frontmatter = split_into_sections(self._frontmatter_raw)
        self._praxis = split_into_sections(self._praxis_raw)
        self._assessment = split_into_sections(self._assessment_raw)
    
        self._frontmatter = normalize_data(self._frontmatter, 'frontmatter')
        self._praxis = normalize_data(self._praxis, 'theory-to-practice')
        self._assessment = normalize_data(self._assessment, 'assessment')

    @property
    def frontmatter(self):
        return self._frontmatter

    @property
    def frontmatter_sections(self):
        return {x: self._frontmatter_sections[x] for x in self._frontmatter}
        

    @property
    def praxis(self):
        return self._praxis

    def praxis_sections(self):
        return {x: self._praxis_sections[x] for x in self._praxis}

    @property
    def assessment(self):
        return self._assessment
        
        
    def _get_raw_content(self):
        return({'meta': {
                'raw_urls': {
                    'frontmatter': self.frontmatter_path,
                    'praxis': self.praxis_path,
                    'assessment': self.assessment_path
                },
                'repo_url': self.repo,
                'user': self.user,
                'repo_name': self.repo_name,
                'branch': self.branch,
            },
            'content': {
                'frontmatter': self._get_live_text_from_url(self.frontmatter_path),
                'theory-to-practice': self._get_live_text_from_url(self.praxis_path),
                'assessment': self._get_live_text_from_url(self.assessment_path),
            }
        })

    def _get_live_text_from_url(self, url):
        """ # TODO: insert docstring here """
        from requests.exceptions import HTTPError

        r = requests.get(url)

        try:
            r.raise_for_status()
        except HTTPError:
            log.error(f'The URL ({url}) could not be used. Verify that you are using the correct repository, and that the branch that you provide is correct.', raise_error=HTTPError)
        return(r.text)

    def _verify_repo(self):
        """ Verifies that a provided repository string is correct. Returns a string with corrected information """

        # TODO: This function doubles up with verify_url() from .meta

        if self.repo == None or self.repo=="" or not isinstance(self.repo, str):
            log.error('No repository URL provided.', raise_error=UnresolvedNameOrBranch)

        if self.repo.endswith('/'):
            self.repo = self.repo[:-1]

        if len(self.repo.split('/')) != 5:
            log.error(f'Cannot interpret repository URL {self.repo}. Are you sure it is a simple https://github.com/user-name/repo link?', raise_error=UnresolvedNameOrBranch)

    def __str__(self):
        return self.meta

    def __repr__(self):
        return f'Loader(repo="{self.repo}", branch="{self.branch}", download={self.download})'



class LoaderCache():
    """ A file cache for the Loader class. """
    
    def __init__(self, repo_name):
        self.repo_name = repo_name
        self.path = DOWNLOAD_CACHE_DIR / (self.repo_name + ".json")
        self.exists = self._check_age()
        
        
    @property
    def data(self):
        if self.exists:
            return self.load_cache()
        else:
            return False
        
        
    def _check_age(self) -> bool:
        if not self.path.exists(): return(False)
        file_mod_time = datetime.fromtimestamp(self.path.stat().st_ctime)
        now = datetime.today()

        if now - file_mod_time > TEST_AGE:
            log.log(f"Cache has expired - older than {TEST_AGE} minutes... Removing.")
            self.path.unlink()
            return False
        else:
            return True
        
        
    def load_cache(self):
        log.log("loading cache...")
        return(json.loads(self.path.read_text()))
        
        
    def save_cache(self, *args, **kwargs):
        log.log("saving cache...")
        if len(args) == 2:
            data = args[1]
            self.path.write_text(json.dumps(data))

            
    def __str__(self):
        return str(self.path)
    
    
    def __repr__(self):
        return f'LoaderCache("{self.repo_name}")'
    
    