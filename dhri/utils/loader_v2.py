# An upgraded and better (faster) loader

from pathlib import Path
import json
import re
import requests
from requests.exceptions import HTTPError, MissingSchema
import markdown, datetime
from dhri.django import django
from dhri.django.models import Workshop, Praxis, Tutorial, Reading, Frontmatter, LearningObjective, Project, Contributor
from dhri.utils.markdown import split_into_sections
from dhri.utils.markdown import Markdown as dhri_Markdown
from dhri.utils.parse_lesson import LessonParser
from dhri.settings import NORMALIZING_SECTIONS, FORCE_DOWNLOAD, BACKEND_AUTO, REPO_AUTO, BRANCH_AUTO
from dhri.constants import TEST_AGES, CACHE_DIRS
from dhri.interaction import Logger

'''
BRANCH_AUTO = 'v2.0-rafa-edits'
REPO_AUTO = 'https://www.github.com/DHRI-Curriculum/text-analysis'
FORCE_DOWNLOAD = False
'''

md_to_html_parser = markdown.Markdown(extensions=['extra', 'codehilite', 'sane_lists', 'nl2br'])



LIST_ELEMENTS = r'- ((?:.*)(?:(?:\n\s{2,4})?(?:.*))*)'
all_list_elements = re.compile(LIST_ELEMENTS)



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


def as_list(md):
    """Returns a string of markdown as a Python list"""
    if not md: return []
    return(all_list_elements.findall(md))


def _is_expired(path, age_checker=TEST_AGES['ROOT']) -> bool:
    """Checks the age for any path against a set expiration date (a timedelta)"""
    if isinstance(path, str): path = Path(path)
    log = Logger(name='cache-age-check')
    if not path.exists() or FORCE_DOWNLOAD == True: return(False)
    file_mod_time = datetime.datetime.fromtimestamp(path.stat().st_ctime)
    now = datetime.datetime.today()

    if now - file_mod_time > age_checker:
        log.warning(f'Cache has expired for {path} - older than {age_checker}...')
        return False
    else:
        log.log(f'Cache is fine for {path} - not older than {age_checker}....')
        return True


def clear_cache():
    """Clears out the cache folder"""
    for DIR in CACHE_DIRS:
        for file in CACHE_DIRS[DIR].glob('*.txt'):
            if _is_expired(file, TEST_AGES[DIR]) == False:
                file.unlink()

        for file in CACHE_DIRS[DIR].glob('*.json'):
            if _is_expired(file, TEST_AGES[DIR]) == False:
                file.unlink()

clear_cache()



class LoaderCache():

    def __init__(self, loader):
        self.loader = loader

        self.path = CACHE_DIRS['ROOT'] / (self.loader.repo_name + ".json")

        if not self.path.exists() or FORCE_DOWNLOAD == True or _is_expired(self.path): self._setup_raw_content()

        self.data = self.load()

        # Set up mapping
        self.frontmatter = self.data.get('frontmatter')
        self.praxis = self.data.get('praxis')
        self.assessment = self.data.get('assessment')
        self.lessons = self.data.get('lessons')


    def _setup_raw_content(self):
        paths = {
            'frontmatter': f'{self.loader.base_url}/frontmatter.md',
            'praxis': f'{self.loader.base_url}/theory-to-practice.md',
            'assessment': f'{self.loader.base_url}/assessment.md',
            'lessons': f'{self.loader.base_url}/lessons.md'
        }
        self.data = {
            'meta': {
                'raw_urls': {
                    'frontmatter': paths['frontmatter'],
                    'praxis': paths['praxis'],
                    'assessment': paths['assessment'],
                    'lessons': paths['lessons']
                },
                'repo_url': self.loader.repo,
                'user': self.loader.user,
                'repo_name': self.loader.repo_name,
                'branch': self.loader.branch,
            },
            'content': {
                'frontmatter': self._load_raw_text(paths['frontmatter']),
                'praxis': self._load_raw_text(paths['praxis']),
                'assessment': self._load_raw_text(paths['assessment']),
                'lessons': self._load_raw_text(paths['lessons'])
            }
        }
        self.save()


    def save(self):
        if not self.path.parent.exists(): self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps(self.data))


    def load(self):
        return json.loads(self.path.read_text())


    def _load_raw_text(self, url:str):
        try:
            r = requests.get(url)
        except MissingSchema:
            self.loader.log.warning("Error: Incorrect URL", kill=False)
            return("")

        try:
            r.raise_for_status()
        except HTTPError:
            self.loader.log.error(f'The URL ({url}) could not be used. Verify that you are using the correct repository, and that the branch that you provide is correct.', raise_error=HTTPError)

        return(r.text)



class HTMLParser():

    def __init__(self, loader):
        self.content = {k: md_to_html_parser.convert(v) for k, v in loader.content.items()}
        self.lessons = loader.lessons
        for i, lesson in enumerate(self.lessons):
            self.lessons[i]['text'] = md_to_html_parser.convert(self.lessons[i]['text'])
            if self.lessons[i]['challenge']: self.lessons[i]['challenge'] = md_to_html_parser.convert(self.lessons[i]['challenge'])
            if self.lessons[i]['solution']: self.lessons[i]['solution'] = md_to_html_parser.convert(self.lessons[i]['solution'])
        self.frontmatter = self.content.get('frontmatter')
        self.praxis = self.content.get('praxis')
        self.assessment = self.content.get('assessment')



class Loader():

    _frontmatter_sections = SECTIONS['frontmatter']
    _praxis_sections = SECTIONS['praxis']
    _assessment_sections = SECTIONS['assessment']

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

    # TODO: Include _assessment_sections test here?

    def _normalize_data(self, data, section):
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
                        file = category
                        if category == 'praxis': file = 'theory-to-practice'
                        msg = f"The file `{file}.md` in repository `{self.repo_name}` contains no section `{section}`."
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


    def __init__(self, repo=REPO_AUTO, branch=BRANCH_AUTO, download=True, force_download=FORCE_DOWNLOAD):

        self.log = Logger(name=f'loader')

        self.branch = branch
        self.download = download
        self.force_download = force_download

        self.repo = repo
        self.user = self.repo.split('/')[3]
        self.repo_name = self.repo.split('/')[4]

        self.parent_backend = BACKEND_AUTO
        self.parent_repo = f'{self.user}/{self.repo_name}'
        self.parent_branch = self.branch

        self.base_url = f'https://raw.githubusercontent.com/{self.user}/{self.repo_name}/{self.branch}'

        self.cache = LoaderCache(self)

        self.data = self.cache.data

        # Map properties
        self.content = self.data.get('content')
        self.meta = self.data.get('meta')

        self.frontmatter = split_into_sections(self.content.get('frontmatter'))
        self.praxis = split_into_sections(self.content.get('praxis'))
        self.assessment = split_into_sections(self.content.get('assessment'))
        self.lessons = LessonParser(self.content.get('lessons'), loader=self).data

        self.frontmatter = self._normalize_data(self.frontmatter, 'frontmatter')
        self.praxis = self._normalize_data(self.praxis, 'theory-to-practice')
        self.assessment = self._normalize_data(self.assessment, 'assessment')

        self.as_html = HTMLParser(self)

        self.content = {
            'frontmatter': self.frontmatter,
            'praxis': self.praxis,
            'assessment': self.assessment,
            'lessons': self.lessons
        }

        self._test_for_required_sections()

        self.has_frontmatter = len(self.frontmatter) > 0
        self.has_praxis = len(self.praxis) > 0
        self.has_assessment = len(self.assessment) > 0
        self.has_lessons = len(self.lessons) > 0


        # Mapping frontmatter sections
        self.abstract = self.frontmatter.get('abstract')
        self.learning_objectives = as_list(self.frontmatter.get('learning_objectives'))
        self.estimated_time = self.frontmatter.get('estimated_time')
        self.contributors = ContributorParser(self.frontmatter.get('contributors')).data
        self.ethical_considerations = as_list(self.frontmatter.get('ethical_considerations'))
        self.readings = as_list(self.frontmatter.get('readings'))
        self.projects = as_list(self.frontmatter.get('projects'))

        # Mapping praxis sections
        self.discussion_questions = as_list(self.praxis.get('discussion_questions'))
        self.next_steps = as_list(self.praxis.get('next_steps'))
        self.tutorials = as_list(self.praxis.get('tutorials'))
        self.further_readings = as_list(self.praxis.get('further_readings'))


class ContributorParser():

    def __init__(self, md:str):
        self.md = md
        self.data = []
        self.process()

    def process(self):
        from dhri.utils.regex import all_links
        md_as_list = as_list(self.md)
        if not len(md_as_list):
            md_as_list = self.md.split("\n")

        for item in md_as_list:
            role = None
            g = all_links.search(item)
            if g:
                _, name, url = g.groups()
                if ":" in name:
                    elems = [_.strip() for _ in name.split(":")]
                    role = elems[0]
                    name = " ".join(elems[1:])
                first_name, last_name = self.split_names(name)
                self.data.append({
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role,
                    'url': url,
                })
            else:
                if ":" in item:
                    elems = [_.strip() for _ in item.split(":")]
                    role = elems[0]
                    name = " ".join(elems[1:])
                    first_name, last_name = self.split_names(name)
                    self.data.append({
                        'first_name': first_name,
                        'last_name': last_name,
                        'role': role,
                        'url': None,
                    })
                else:
                    first_name, last_name = self.split_names(item)
                    self.data.append({
                        'first_name': first_name,
                        'last_name': last_name,
                        'role': None,
                        'url': None,
                    })

    def split_names(self, full_name:str) -> tuple:
        """Uses the `nameparser` library to interpret names."""

        from nameparser import HumanName

        name = HumanName(full_name)
        first_name = name.first
        if name.middle:
            first_name += " " + name.middle
        last_name = name.last
        return((first_name, last_name))
