import requests, json, datetime
from dhri.django import django
from dhri.django.models import Workshop, Praxis, Tutorial, Reading, Frontmatter, LearningObjective, Project, Contributor
from dhri.interaction import Logger
from dhri.utils.markdown import split_into_sections, get_contributors, Markdown
from dhri.utils.exceptions import UnresolvedNameOrBranch, MissingCurriculumFile, MissingRequiredSection

from dhri.settings import NORMALIZING_SECTIONS, REPO_AUTO, BRANCH_AUTO, BACKEND_AUTO, FORCE_DOWNLOAD
from dhri.constants import DOWNLOAD_CACHE_DIR, TEST_AGE

from django.utils.text import slugify
from pathlib import Path

log = Logger(name='loader')

SECTIONS = {
    'frontmatter': {
        'abstract': (Frontmatter, True),
        'learning_objectives': (LearningObjective, False),
        'estimated_time': (Frontmatter, False),
        'contributors': (Contributor, False),
        'ethical_considerations': (Frontmatter, False),
        'readings': (Reading, False),
        'projects': (Project, False),
    },
    'praxis': {
        'discussion_questions': (Praxis, False),
        'next_steps': (Praxis, False),
        'tutorials': (Tutorial, False),
        'further_readings': (Reading, False),
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

    log = Logger(name='loader')

    _frontmatter_sections = SECTIONS['frontmatter']

    _praxis_sections = SECTIONS['praxis']

    frontmatter_models = {}
    for section, item in _frontmatter_sections.items():
        model, required = item
        if not model in frontmatter_models: frontmatter_models[model] = []
        frontmatter_models[model].append(section)

    praxis_models = {}
    for section, item in _praxis_sections.items():
        model, required = item
        if not model in praxis_models: praxis_models[model] = []
        praxis_models[model].append(section)


    def __init__(self, repo=REPO_AUTO, branch=BRANCH_AUTO, download=True, force_download=FORCE_DOWNLOAD):
        self.repo = repo
        self.branch = branch
        self.download = download

        self._verify_repo()

        self.user = self.repo.split('/')[3]
        self.repo_name = self.repo.split('/')[4]

        self.log.name = self.repo_name + '-load'

        self.log.log(f'Loading content {self.repo_name}...')

        self.name = self.repo_name.replace('-', '').title().replace(' And ', ' and ')

        self.cache = LoaderCache(self.repo_name, self)

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
        self.parent_repo = f'{self.user}/{self.repo_name}'
        self.parent_branch = self.branch
        self._content_raw = self._raw_content['content']

        self._frontmatter_raw = self._content_raw.get('frontmatter')
        self._praxis_raw = self._content_raw.get('praxis')
        self._assessment_raw = self._content_raw.get('assessment')

        self._frontmatter = split_into_sections(self._frontmatter_raw)
        self._praxis = split_into_sections(self._praxis_raw)
        self._assessment = split_into_sections(self._assessment_raw)

        self._frontmatter = normalize_data(self._frontmatter, 'frontmatter')
        self._praxis = normalize_data(self._praxis, 'theory-to-practice')
        self._assessment = normalize_data(self._assessment, 'assessment')

        self.content = {
            'frontmatter': self._frontmatter,
            'praxis': self._praxis,
            'assessment': self._assessment,
        }

        self._test_for_required_sections()


    def _test_for_required_sections(self):
        for category in SECTIONS:
            for section, item in SECTIONS[category].items():
                _, required = item
                cat_data = self.content.get(category)
                if cat_data != None:
                    section_data = cat_data.get(section)
                    if section_data:
                        pass # we have section_data
                    else:
                        msg = f"category `{category}` in repository {self.repo_name}'s {category}.md contains no section `{section}`."
                        if required:
                            msg = msg.replace('`.', ' (required).')
                            self.log.error(msg, raise_error=MissingRequiredSection)
                        else:
                            self.log.warning(msg)
                else:
                    if category == 'praxis': category = 'theory-to-practice' # because it is differently named...
                    msg = f'`{category}.md` appears to not exist in the repository {self.repo_name}.'
                    if required:
                        self.log.error(msg, raise_error=MissingCurriculumFile)
                    else:
                        self.log.warning(msg)


    @property
    def has_frontmatter(self) -> bool:
        return len(self._frontmatter) > 0

    @property
    def has_praxis(self) -> bool:
        return len(self.praxis) > 0

    @property
    def has_assessment(self) -> bool:
        return len(self._assessment) > 0


    @property
    def frontmatter(self):
        return self._frontmatter

    @property
    def frontmatter_sections(self):
        return {x: self._frontmatter_sections[x] for x in self._frontmatter}

    @property
    def abstract(self):
        return self.frontmatter.get('abstract', '')

    @property
    def has_abstract(self) -> bool:
        return self.abstract != None and self.abstract != []

    @property
    def learning_objectives(self):
        return(Markdown(text=self.frontmatter.get('learning_objectives', ''))) # I believe this now handles being an "empty list" if iterated through empty

    @property
    def has_learning_objectives(self) -> bool:
        return self.learning_objectives != None and self.learning_objectives != []

    @property
    def estimated_time(self):
        return self.frontmatter.get('estimated_time', '')

    @property
    def has_estimated_time(self) -> bool:
        return self.estimated_time != None and self.estimated_time != []

    @property
    def contributors(self):
        return(Markdown(text=self.frontmatter.get('contributors', '')).as_contributors())

    @property
    def has_contributors(self) -> bool:
        return self.contributors != None and self.contributors != []

    @property
    def ethical_considerations(self):
        return self.frontmatter.get('ethical_considerations', '')

    @property
    def has_ethical_considerations(self) -> bool:
        return self.ethical_considerations != None and self.ethical_considerations != []

    @property
    def readings(self):
        return(Markdown(text=self.frontmatter.get('readings', '')))

    @property
    def has_readings(self) -> bool:
        return self.readings != None and self.readings != []

    @property
    def projects(self):
        return(Markdown(text=self.frontmatter.get('projects', ''))) # I believe this now handles being an "empty list" if iterated through empty

    @property
    def has_projects(self):
        return self.projects != None and self.projects != []


    @property
    def praxis(self):
        return self._praxis

    def praxis_sections(self):
        return {x: self._praxis_sections[x] for x in self._praxis}

    @property
    def discussion_questions(self):
        return(Markdown(text=self.praxis.get('discussion_questions', '')))

    @property
    def has_discussion_questions(self) -> bool:
        return self.discussion_questions != None and self.discussion_questions != []

    @property
    def next_steps(self):
        return(Markdown(text=self.praxis.get('next_steps', '')))
        # return self.praxis.get('next_steps', '')

    @property
    def has_next_steps(self) -> bool:
        return self.next_steps != None and self.next_steps != []

    @property
    def tutorials(self) -> list:
        return(Markdown(text=self.praxis.get('tutorials', ''))) # I believe this now handles being an "empty list" if iterated through empty

    @property
    def has_tutorials(self) -> bool:
        return self.tutorials != None and self.tutorials != []

    @property
    def further_readings(self):
        return(Markdown(text=self.praxis.get('further_readings', ''))) # I believe this now handles being an "empty list" if iterated through empty

    @property
    def has_further_readings(self) -> bool:
        return self.further_readings != None and self.further_readings != []


    @property
    def assessment(self):
        return self._assessment

    # FIXME: #3


    def _get_raw_content(self):
        """Internal method to get all the sections and return a dict with all the relevant information for the repository"""

        try:
          frontmatter_data = self._get_live_text_from_url(self.frontmatter_path)
        except:
          self.log.warning(f'Could not load frontmatter data from repository {self.repo_name}. Please verify that its branch {self.branch} contains frontmatter.md.', color='red')
          frontmatter_data = ''

        try:
          praxis_data = self._get_live_text_from_url(self.praxis_path)
        except:
          self.log.warning(f'Could not load theory-to-practice data from repository {self.repo_name}. Please verify that its branch {self.branch} contains theory-to-practice.md.', color='red')
          praxis_data = ''

        try:
          assessment_data = self._get_live_text_from_url(self.assessment_path)
        except:
          self.log.warning(f'Could not load assessment data from repository {self.repo_name}. Please verify that its branch {self.branch} contains assessment.md.', color='red')
          assessment_data = ''

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
                'praxis': praxis_data,
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
            self.log.error(f'The URL ({url}) could not be used. Verify that you are using the correct repository, and that the branch that you provide is correct.', raise_error=HTTPError)

        return(r.text)


    def _verify_repo(self):
        """ Verifies that a provided repository string is correct. Sets self.repo to a string with corrected information """

        if self.repo == None or self.repo=='' or not isinstance(self.repo, str):
            self.log.error('No repository URL provided.', raise_error=UnresolvedNameOrBranch)

        if self.repo.endswith('/'):
            self.repo = self.repo[:-1]

        if len(self.repo.split('/')) != 5:
            self.log.error(f'Cannot interpret repository URL {self.repo}. Are you sure it is a simple https://github.com/user-name/repo link?', raise_error=UnresolvedNameOrBranch)


    def __str__(self):
        return self.meta


    def __repr__(self):
        return f'Loader(repo="{self.repo}", branch="{self.branch}", download={self.download})'



class LoaderCache():
    """ A file cache for the Loader class. """

    def __init__(self, repo_name:str, loader:Loader):
        self.repo_name = repo_name
        self.path = DOWNLOAD_CACHE_DIR / (self.repo_name + '.json')
        self.exists = self._check_age()
        self.parent = loader

    @property
    def data(self):
        if self.exists:
            return self.load_cache()
        else:
            return False

    def _check_age(self) -> bool:
        if not self.path.exists(): return(False)
        file_mod_time = datetime.datetime.fromtimestamp(self.path.stat().st_ctime)
        now = datetime.datetime.today()

        if now - file_mod_time > TEST_AGE:
            try:
                self.parent.log.log(f'Cache has expired - older than {TEST_AGE} minutes... Removing.')
            except:
                log.log(f'Cache has expired - older than {TEST_AGE} minutes... Removing.')
            self.path.unlink()
            return False
        else:
            return True


    def load_cache(self) -> dict:
        try:
            self.parent.log.log('Loading cache from local file.')
        except:
            log.log('Loading cache from local file.')
        return(json.loads(self.path.read_text()))


    def save_cache(self, *args, **kwargs) -> bool:
        try:
            self.parent.log.log(f'Saving cache locally: Cache path is {self.path}')
        except:
            log.log(f'Saving cache locally: Cache path is {self.path}')
        if len(args) == 2:
            data = args[1]
            if not self.path.parent.exists(): self.path.parent.mkdir(parents=True)
            self.path.write_text(json.dumps(data))
        return(True)


    def __str__(self) -> str:
        return f'{self.path}'


    def __repr__(self) -> str:
        return f'LoaderCache("{self.repo_name}")'



class WebCache(LoaderCache):

    def __init__(self, url:str, force_download=FORCE_DOWNLOAD):

        self.url = url
        self.title = None
        self.force_download = FORCE_DOWNLOAD

        if url != None and str(url).lower().strip() != 'none' and str(url).lower().strip() != '':
            self.path = DOWNLOAD_CACHE_DIR / (slugify(url[:100])+'.txt')
            self.path = Path(self.path)

            self._check_age()

            if not self.path.exists():
                title = self.try_title_element_from_url()
                self.path.write_text(title)

            if self.path.exists():
                self.title = self.path.read_text()

    def try_title_element_from_url(self):
        import requests
        from bs4 import BeautifulSoup

        if self.url != None and str(self.url).lower().strip() == 'none' and str(self.url).lower().strip() == '':
            return('')
        else:
            log.warning(f'Trying to download title from web page...')
            if not self.url.startswith('http'):
                self.url = f'http://{self.url}'
            #try:
            r = requests.get(self.url)
            soup = BeautifulSoup(r.text, 'lxml')
            try:
                return(soup.find('title').text)
            except:
                return('')

    def _check_age(self) -> bool:
        if not self.path.exists() or self.force_download == True: return(False)
        file_mod_time = datetime.datetime.fromtimestamp(self.path.stat().st_ctime)
        now = datetime.datetime.today()

        if now - file_mod_time > TEST_AGE:
            try:
                self.parent.log.log(f'Cache has expired - older than {TEST_AGE} minutes... Removing.')
            except:
                log.log(f'Cache has expired - older than {TEST_AGE} minutes... Removing.')
            self.path.unlink()
            return False
        else:
            return True