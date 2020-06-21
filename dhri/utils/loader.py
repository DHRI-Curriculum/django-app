import requests, json
from datetime import datetime

from dhri.django import django
from dhri.django.models import Workshop, Praxis, Tutorial, Reading, Frontmatter, LearningObjective, Project, Contributor
from dhri.interaction import Logger
from dhri.utils.markdown import split_into_sections
from dhri.utils.exceptions import UnresolvedNameOrBranch

from dhri.settings import NORMALIZING_SECTIONS, REPO_AUTO, BRANCH_AUTO, BACKEND_AUTO, FORCE_DOWNLOAD
from dhri.constants import DOWNLOAD_CACHE_DIR, TEST_AGE

log = Logger(name='loader')

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
        # FIXME #3: add here
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


    def __init__(self, repo=REPO_AUTO, branch=BRANCH_AUTO, download=True, force_download=FORCE_DOWNLOAD):
        self.repo = repo
        self.branch = branch
        self.download = download

        self._verify_repo()

        self.user = self.repo.split('/')[3]
        self.repo_name = self.repo.split('/')[4]

        self.name = self.repo_name.replace('-', '').title().replace(" And ", "and")

        self.cache = LoaderCache(self.repo_name)

        # Set up raw urls
        self._raw_url = f'https://raw.githubusercontent.com/{self.user}/{self.repo_name}/{self.branch}'

        self.frontmatter_path = f'{self._raw_url}/frontmatter.md'
        self.praxis_path = f'{self._raw_url}/theory-to-practice.md'
        self.assessment_path = f'{self._raw_url}/assessment.md'

        if not self.cache.exists or force_download:
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
    def abstract(self):
        return self._frontmatter.get('abstract')

    @property
    def learning_objectives(self):
        return self._frontmatter.get('learning_objectives')

    @property
    def estimated_time(self):
        return self._frontmatter.get('estimated_time')

    @property
    def contributors(self):
        return self._frontmatter.get('contributors')

    @property
    def ethical_considerations(self):
        return self._frontmatter.get('ethical_considerations')

    @property
    def readings(self):
        return self._frontmatter.get('readings')

    @property
    def project(self):
        return self._frontmatter.get('project')


    @property
    def praxis(self):
        return self._praxis

    def praxis_sections(self):
        return {x: self._praxis_sections[x] for x in self._praxis}

    @property
    def discussion_questions(self):
        return self._frontmatter.get('discussion_questions')

    @property
    def next_steps(self):
        return self._frontmatter.get('tutorials')

    @property
    def discussion_questions(self):
        return self._frontmatter.get('tutorials')

    @property
    def further_readings(self):
        return self._frontmatter.get('further_readings')

    @property
    def assessment(self):
        return self._assessment

    # TODO: #3


    def _get_raw_content(self):
        """Internal method to get all the sections and return a dict with all the relevant information for the repository"""
        try:
          frontmatter_data = self._get_live_text_from_url(self.frontmatter_path)
        except:
          log.warning(f"Could not load frontmatter data from repository {self.repo_name}. Please verify that its branch {self.branch} contains frontmatter.md.", color='red')
          frontmatter_data = ""

        try:
          praxis_data = self._get_live_text_from_url(self.praxis_path)
        except:
          log.warning(f"Could not load theory-to-practice data from repository {self.repo_name}. Please verify that its branch {self.branch} contains theory-to-practice.md.", color='red')
          praxis_data = ""

        try:
          assessment_data = self._get_live_text_from_url(self.assessment_path)
        except:
          log.warning(f"Could not load assessment data from repository {self.repo_name}. Please verify that its branch {self.branch} contains assessment.md.", color='red')
          assessment_data = ""

        return({
            'meta': {
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
                'frontmatter': frontmatter_data,
                'theory-to-practice': praxis_data,
                'assessment': assessment_data,
            }
        })


    def _get_live_text_from_url(self, url:str) -> str:
        """Downloads the live text from a given URL and returns it."""
        from requests.exceptions import HTTPError

        r = requests.get(url)

        try:
            r.raise_for_status()
        except HTTPError:
            log.error(f'The URL ({url}) could not be used. Verify that you are using the correct repository, and that the branch that you provide is correct.', raise_error=HTTPError)

        return(r.text)


    def _verify_repo(self):
        """ Verifies that a provided repository string is correct. Sets self.repo to a string with corrected information """

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


    def load_cache(self) -> dict:
        log.log("loading cache...")
        return(json.loads(self.path.read_text()))


    def save_cache(self, *args, **kwargs) -> bool:
        log.log("saving cache...")
        if len(args) == 2:
            data = args[1]
            self.path.write_text(json.dumps(data))
        return(True)


    def __str__(self) -> str:
        return f"{self.path}"


    def __repr__(self) -> str:
        return f'LoaderCache("{self.repo_name}")'
