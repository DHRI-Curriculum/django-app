"""Loader functionality for DHRI Curriculum"""


import datetime
import json
import requests
import re

from pathlib import Path
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, MissingSchema

from django.urls import reverse

from backend.models import *

from backend.dhri.exceptions import MissingCurriculumFile, MissingRequiredSection
from backend.dhri.log import Logger, get_or_default
from backend.dhri.markdown import split_into_sections, as_list, extract_links
from backend.dhri.markdown_parser import PARSER
from backend.dhri.text import get_number
from backend.dhri.webcache import WebCache

from backend.dhri_settings import NORMALIZING_SECTIONS, FORCE_DOWNLOAD, BACKEND_AUTO, \
                                    REPO_AUTO, BRANCH_AUTO, TEST_AGES, CACHE_DIRS, \
                                    STATIC_IMAGES, LESSON_TRANSPOSITIONS, VERBOSE, CACHE_VERBOSE, TERMINAL_WIDTH

from backend.dhri.new_functions import mini_parse_eval, mini_parse_keywords


log = Logger(name='loader')


SECTIONS = {
    'frontmatter': {
        'abstract': (Frontmatter, True),
        'learning_objectives': (LearningObjective, False),
        'estimated_time': (Frontmatter, False),
        'contributors': (Contributor, False),
        'ethical_considerations': (EthicalConsideration, False),
        'readings': (Reading, False),
        'projects': (Project, False),
    },
    'praxis': {
        'intro': (Praxis, False),
        'discussion_questions': (DiscussionQuestion, False),
        'next_steps': (NextStep, False),
        'tutorials': (Tutorial, False),
        'further_readings': (Reading, False),
        'further_projects': (Project, False),
    },
    'assessment': {
        # FIXME #3: add here
    }
}


def _is_expired(path, age_checker=TEST_AGES['ROOT'], force_download=FORCE_DOWNLOAD) -> bool:
    """Checks the age for any path against a set expiration date (a timedelta)"""

    if isinstance(path, str): path = Path(path)
    log = Logger(name='cache-age-check')
    if not path.exists() or force_download == True: return(True)
    file_mod_time = datetime.datetime.fromtimestamp(path.stat().st_ctime)
    now = datetime.datetime.today()

    if now - file_mod_time > age_checker:
        log.warning(f'Cache has expired for {path} - older than {age_checker}...')
        return True

    if CACHE_VERBOSE == True: log.log(f'Cache is OK for {path} - not older than {age_checker}....', force=True)
    return False


def process_links(input, obj, is_html=False) -> tuple:
    """<#TODO: docstr>"""
    title, url = None, None
    if is_html == False:
        links = extract_links(input)
        if links:
            title, url = links[0]
        else:
            return(None, None)
    else:
        soup = BeautifulSoup(input, 'lxml')
        links = soup.find_all("a")
        if not len(links):
            log.warning(f'A link was expected in the input but could not be parsed: {input}')
            return(None, None)
        title, url = links[0].text, links[0]['href']

    if len(links) > 1:
        if is_html:
            url_list = [x['href'] for x in links]
            url_list.insert(0,'*** '+url)
            link_list = '- ' + "\n    - ".join([x[:TERMINAL_WIDTH-30] for x in url_list])
        else:
            links = [x[1] for x in links]
            links[0] = '*** '+links[0]
            link_list = '- ' + "\n    - ".join([x[:TERMINAL_WIDTH-30] for x in links])
        log.warning(f'One project seems to contain more than one URL, but only the first is captured:' + link_list) # TODO: Better handling of this in general....
    if title == None or title == '':
        from backend.dhri.webcache import WebCache
        title = WebCache(url).title
        title = get_or_default(f'Set a title for the {obj} at {url}: ', title)
    return(title, url)


def clear_cache():
    """Clears out the cache folder"""

    for DIR in CACHE_DIRS:
        for file in CACHE_DIRS[DIR].glob('*.txt'):
            if _is_expired(file, TEST_AGES[DIR]) == True:
                file.unlink()

        for file in CACHE_DIRS[DIR].glob('*.json'):
            if _is_expired(file, TEST_AGES[DIR]) == True:
                file.unlink()

clear_cache()



class LoaderCache():
    """Handles all the live loading of DHRI Curriculum data from GitHub"""

    def __init__(self, loader, force_download=FORCE_DOWNLOAD):
        self.loader = loader

        self.path = CACHE_DIRS['ROOT'] / (self.loader.repo_name + ".json")

        if not self.path.exists() or force_download == True or _is_expired(self.path, force_download=force_download) == True: self._setup_raw_content()

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
            'lessons': f'{self.loader.base_url}/lessons.md',
            'image': f'{self.loader.base_url}/image.md'
        }
        self.data = {
            'meta': {
                'raw_urls': {
                    'frontmatter': paths['frontmatter'],
                    'praxis': paths['praxis'],
                    'assessment': paths['assessment'],
                    'lessons': paths['lessons'],
                    'image': paths['image'],
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
                'lessons': self._load_raw_text(paths['lessons']),
                'image': self._load_raw_text(paths['image'])
            }
        }
        self.save()


    def save(self):
        """Saves <self.data> into <self.path>"""
        if not self.path.parent.exists(): self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps(self.data))


    def load(self):
        """Loads <self.data> from <self.path>"""
        return json.loads(self.path.read_text())


    def _load_raw_text(self, url:str):
        """Downloads the raw text from a given URL and generates appropriate errors if it fails"""
        try:
            r = requests.get(url)
        except MissingSchema:
            self.loader.log.warning("Error: Incorrect URL", kill=False)
            return("")

        try:
            r.raise_for_status()
        except HTTPError:
            self.loader.log.error(f'The URL ({url}) could not be used. Verify that you are using the correct repository, and that the branch that you provide is correct and that it contains all the required files.', raise_error=HTTPError)

        return(r.text)


class HTMLParser(): # pylint: disable=too-few-public-methods
    """Parses any given Loader data into HTML through the Markdown module"""

    def __init__(self, loader):
        self.content = {k: PARSER.convert(v) for k, v in loader.content.items()}
        self.lessons = loader.lessons_html
        '''
        for i, lesson in enumerate(self.lessons):
            self.lessons[i]['text'] = PARSER.convert(self.lessons[i]['text'])
            if self.lessons[i]['challenge']: self.lessons[i]['challenge'] = PARSER.convert(self.lessons[i]['challenge'])
            if self.lessons[i]['solution']: self.lessons[i]['solution'] = PARSER.convert(self.lessons[i]['solution'])
        '''
        self.frontmatter = self.content.get('frontmatter')
        self.praxis = self.content.get('praxis')
        self.assessment = self.content.get('assessment')
        self.image = PARSER.convert(self.content.get('image'))


def _normalize_data(data, section):
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
    """Loading DHRI Curriculum cache files into parsable dictionaries inside an object"""

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

    # TODO: #364 Include _assessment_sections test here?


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

    def _test_for_files(self):
        if sum([self.has_frontmatter, self.has_praxis, self.has_lessons, self.has_assessment]) <= 3:
            msg = f"The repository {self.repo_name} does not have enough required files present. The import of the entire repository will be skipped."
            self.log.error(msg, raise_error=MissingCurriculumFile)

    def __init__(self, repo=REPO_AUTO, branch=BRANCH_AUTO, force_download=FORCE_DOWNLOAD):

        self.log = Logger(name=f'loader')

        if not repo.startswith('https://github.com/'):
            log.error('Repository URL does not look correct. Needs to start with https://github.com/')

        self.branch = branch
        self.repo = repo
        self.user = self.repo.split('/')[3]
        self.repo_name = self.repo.split('/')[4]

        self.parent_backend = BACKEND_AUTO
        self.parent_repo = f'{self.user}/{self.repo_name}'
        self.parent_branch = self.branch

        self.base_url = f'https://raw.githubusercontent.com/{self.user}/{self.repo_name}/{self.branch}'

        self.data = LoaderCache(self, force_download=force_download).data

        # Map properties
        self.content = self.data.get('content')
        self.meta = self.data.get('meta')

        self.frontmatter = split_into_sections(self.content.get('frontmatter'))
        self.praxis = split_into_sections(self.content.get('praxis'))
        self.assessment = split_into_sections(self.content.get('assessment'))
        self.image = self.content.get('image')
        self.lessons = LessonParser(self.content.get('lessons'), loader=self).data
        self.lessons_html = LessonParser(self.content.get('lessons'), loader=self).html_data

        self.frontmatter = _normalize_data(self.frontmatter, 'frontmatter')
        self.praxis = _normalize_data(self.praxis, 'theory-to-practice')
        self.assessment = _normalize_data(self.assessment, 'assessment')

        # fix frontmatter data sections
        self.frontmatter['estimated_time'] = get_number(self.frontmatter.get('estimated_time'))
        self.frontmatter['contributors'] = ContributorParser(self.frontmatter.get('contributors')).data
        self.frontmatter['readings'] = [str(_) for _ in as_list(self.frontmatter.get('readings'))]
        self.frontmatter['projects'] = [str(_) for _ in as_list(self.frontmatter.get('projects'))]
        self.frontmatter['learning_objectives'] = [PARSER.convert(_) for _ in as_list(self.frontmatter.get('learning_objectives'))] # make into HTML
        self.frontmatter['ethical_considerations'] = [PARSER.convert(_) for _ in as_list(self.frontmatter.get('ethical_considerations'))]
        self.frontmatter['prerequisites'] = [PARSER.convert(_) for _ in as_list(self.frontmatter.get('prerequisites'))]
        self.frontmatter['resources'] = [_ for _ in as_list(self.frontmatter.get('resources'))]

        # fix praxis data sections
        self.praxis['discussion_questions'] = [str(_) for _ in as_list(self.praxis.get('discussion_questions'))]
        self.praxis['next_steps'] = [str(_) for _ in as_list(self.praxis.get('next_steps'))]
        self.praxis['tutorials'] = [str(_) for _ in as_list(self.praxis.get('tutorials'))]
        self.praxis['further_readings'] = [str(_) for _ in as_list(self.praxis.get('further_readings'))]
        self.praxis['further_projects'] = [str(_) for _ in as_list(self.praxis.get('further_projects'))]
        self.praxis['more_resources'] = [str(_) for _ in as_list(self.praxis.get('more_resources'))]

        self.as_html = HTMLParser(self)

        self.content = {
            'title': [x for x in split_into_sections(self.content.get('frontmatter'), level_granularity=1)][0],
            'frontmatter': self.frontmatter,
            'praxis': self.praxis,
            'assessment': self.assessment,
            'lessons': self.lessons,
            'image': self.image
        }

        self._test_for_required_sections()

        self.has_frontmatter = len(self.frontmatter) > 0
        self.has_praxis = len(self.praxis) > 0
        self.has_assessment = len(self.assessment) > 0
        self.has_lessons = len(self.lessons) > 0
        self.has_image = len(self.image) > 0

        self._test_for_files()

        # Fixing the image
        REPO_CLEAR = self.repo.split("/")[-1]
        soup = BeautifulSoup(self.as_html.image, 'lxml')
        local_file, local_url = '', ''
        for image in soup.find_all("img")[:1]: # we stick with the first image here.
            src = image.get('src')
            if not src:
                log.warning(f"A header image with no src attribute detected in workshop: {image}")
                continue
            filename = image['src'].split('/')[-1]
            url = f'https://raw.githubusercontent.com/DHRI-Curriculum/{REPO_CLEAR}/{self.branch}/_django-meta/{filename}'
            filename = filename.replace('%40', '@')
            local_file = STATIC_IMAGES['WORKSHOP_HEADERS'] / Path(REPO_CLEAR) / filename

            if '//' in url:
                url = url.replace('//', '/').replace('https:/', 'https://').replace('http:/', 'http://')

            download_image(url, local_file)
            local_url = f'/static/website/images/workshop_headers/{REPO_CLEAR}/{filename}'
            image['src'] = local_url
            image['class'] = image.get('class', []) + ['img-fluid', 'd-block', 'my-4']

        self.image_path = str(local_file)
        self.local_url = local_url
        self.title = self.content.get('title')

        # Mapping frontmatter sections
        self.abstract = self.frontmatter.get('abstract')
        self.estimated_time = self.frontmatter.get('estimated_time')
        self.contributors = self.frontmatter.get('contributors')
        self.readings = self.frontmatter.get('readings')
        self.projects = self.frontmatter.get('projects')
        self.learning_objectives = self.frontmatter.get('learning_objectives')
        self.ethical_considerations = self.frontmatter.get('ethical_considerations')
        self.prerequisites = self.frontmatter.get('prerequisites')
        self.resources = self.frontmatter.get('resources')

        # Mapping praxis sections
        self.praxis_intro = PARSER.convert(self.praxis.get('intro'))
        self.discussion_questions = self.praxis.get('discussion_questions')
        self.next_steps = self.praxis.get('next_steps')
        self.tutorials = self.praxis.get('tutorials')
        self.further_readings = self.praxis.get('further_readings')
        self.further_projects = self.praxis.get('further_projects')
        self.more_resources = self.praxis.get('more_resources')

class ContributorParser():

    def __init__(self, md:str):
        self.md = md
        self.data = []
        self.process()

    def process(self):
        from backend.dhri.regex import all_links
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
                elif ":" in item:
                    elems = [_.strip() for _ in item.split(":")]
                    role = elems[0]
                first_name, last_name = self.split_names(name)

                if first_name == 'Rafael Davis' and last_name == 'Portela': # Correct this name manually
                    first_name = 'Rafael'
                    last_name = 'Davis Portela'

                if not first_name.lower() == 'none' and not first_name == '':
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
                    if not first_name.lower() == 'none' and not first_name == '':
                        self.data.append({
                            'first_name': first_name,
                            'last_name': last_name,
                            'role': role,
                            'url': None,
                        })
                else:
                    first_name, last_name = self.split_names(item)
                    if not first_name.lower() == 'none' and not first_name == '':
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





def download_image(url, local_file):
    if not isinstance(local_file, Path): local_file = Path(local_file)
    if not local_file.parent.exists(): local_file.parent.mkdir(parents=True)
    if not local_file.exists():
        r = requests.get(url)
        if r.status_code == 200:
            with open(local_file, 'wb+') as f:
                for chunk in r:
                    f.write(chunk)
        elif r.status_code == 404:
            url = url.replace('/images/', '/sections/images/')
            r = requests.get(url)
            if r.status_code == 200:
                with open(local_file, 'wb+') as f:
                    for chunk in r:
                        f.write(chunk)
                return local_file
            elif r.status_code == 404:
                log.error(f"Could not download image {local_file.name} (not found): {url}")
                return None
            elif r.status_code == 403:
                log.error(f"Could not download image {local_file.name} (not allowed)")
                return None
        elif r.status_code == 403:
            log.error(f"Could not download image {local_file.name} (not allowed)")
            return None
    else:
        return local_file


def search_term(slug):
    from glossary.models import Term

    t = Term.objects.filter(slug=slug)
    if t:
        return t

    term = slug.replace('-', ' ')
    t = Term.objects.filter(term=term)
    if t:
        return t

    term = term.title()
    t = Term.objects.filter(term=term)
    if t:
        return t

    return None


def search_software(slug):
    from install.models import Software

    t = Software.objects.filter(software__icontains=slug)
    if t:
        return t

    software = slug.replace('-', ' ')
    t = Software.objects.filter(software__icontains=software)
    if t:
        return t

    software = software.title()
    t = Software.objects.filter(software__icontains=software)
    if t:
        return t

    return None


def search_insight(slug):
    from insight.models import Insight

    t = Insight.objects.filter(slug__icontains=slug)
    if t:
        return t

    title = slug.replace('-', ' ')
    t = Insight.objects.filter(title__icontains=title)
    if t:
        return t

    return None



class LessonParser():

    def __init__(self, markdown:str, loader:object):
        self.markdown = markdown

        try:
            self.repo = loader.repo
            self.branch = loader.branch
        except:
            self.repo = None
            self.branch = None
            log.warning('No loader object provided so will not download images from lesson file for repository.')

        self.data = []
        self.html_data = []

        markdown_contents = split_into_sections(self.markdown, level_granularity=1, clear_empty_lines=False)

        for title, body in markdown_contents.items():
            droplines = []

            challenge, challenge_title = "", ""
            # 1. Test markdown for challenge
            if "## challenge" in body.lower() or "## activity" in body.lower():
                for line_num, line in enumerate(body.splitlines()):
                    if line.lower().startswith("## challenge") or line.lower().startswith("## activity"):
                        try:
                            challenge_title = [x.strip() for x in line.split(':') if not x.startswith('#')][0]
                        except IndexError:
                            challenge_title = ''
                        droplines.append(line_num)
                        startline = line_num + 1
                        nextlines = (item for item in body.splitlines()[startline:])
                        done = False
                        while not done:
                            try:
                                l = next(nextlines)
                                if l.startswith("#"):
                                    done = True
                                    continue
                                challenge += l + "\n"
                                droplines.append(startline)
                                startline += 1
                            except StopIteration:
                                done = True

            solution, solution_title = "", ""
            # 2. Test markdown for solution
            if "## solution" in body.lower():
                for line_num, line in enumerate(body.splitlines()):
                    if line.lower().startswith("## solution"):
                        try:
                            solution_title = [x.strip() for x in line.split(':') if not x.startswith('#')][0]
                        except IndexError:
                            solution_title = ''
                        droplines.append(line_num)
                        startline = line_num + 1
                        nextlines = (item for item in body.splitlines()[startline:])
                        done = False
                        while not done:
                            try:
                                l = next(nextlines)
                                if l.startswith("#"):
                                    done = True
                                    continue
                                solution += l + "\n"
                                droplines.append(startline)
                                startline += 1
                            except StopIteration:
                                done = True

            # 3. Evaluation
            evaluation = ""
            if "## evaluation" in body.lower():
                for line_num, line in enumerate(body.splitlines()):
                    if line.lower().startswith("## evaluation"):
                        droplines.append(line_num)
                        startline = line_num + 1
                        nextlines = (item for item in body.splitlines()[startline:])
                        done = False
                        while not done:
                            try:
                                l = next(nextlines)
                                if l.startswith("#"):
                                    done = True
                                    continue
                                evaluation += l + "\n"
                                droplines.append(startline)
                                startline += 1
                            except StopIteration:
                                done = True

            evaluation = mini_parse_eval(evaluation)

            # 4. Glossary terms
            keywords = ""
            if "## keywords" in body.lower():
                for line_num, line in enumerate(body.splitlines()):
                    if line.lower().startswith("## keywords"):
                        droplines.append(line_num)
                        startline = line_num + 1
                        nextlines = (item for item in body.splitlines()[startline:])
                        done = False
                        while not done:
                            try:
                                l = next(nextlines)
                                if l.startswith("#"):
                                    done = True
                                    continue
                                keywords += l + "\n"
                                droplines.append(startline)
                                startline += 1
                            except StopIteration:
                                done = True

            keywords = mini_parse_keywords(keywords)

            # 4. Fix markdown body
            cleaned_body = ''
            for i, line in enumerate(body.splitlines()):
                #if line.strip() == '': continue
                if i not in droplines:
                    cleaned_body += line + '\n'

            #cleaned_body = re.sub(r' +', ' ', cleaned_body)
            #cleaned_body = re.sub(r'\n+', '\n', cleaned_body)

            # 5. Clean up all markdown data
            title = title.strip()
            body = body.strip()
            challenge = challenge.strip()
            solution = solution.strip()

            if challenge == '':
                challenge = None

            if solution == '':
                solution = None

            if solution and not challenge:
                log.error(f"The lesson `{title}` has a solution but no challenge. The program has stopped.")
            elif challenge and not solution:
                pass # This used to be `log.warning(f'The lesson `{title}` has a challenge with no solution.')`

            data = {
                    'title': title,
                    'text': cleaned_body,
                    'challenge': challenge,
                    'challenge_title': challenge_title,
                    'solution': solution,
                    'solution_title': solution_title,
                    'evaluation': evaluation,
                    'keywords': keywords,
                }

            self.data.append(data)

            ####################################################
            # Next up: HTML parsing ############################
            ####################################################

            html_body = PARSER.convert(cleaned_body)
            html_challenge, html_solution = '', ''

            if challenge:
                html_challenge = PARSER.convert(challenge)

            if solution:
                html_solution = PARSER.convert(solution)

            for i, d in enumerate(evaluation):
                evaluation[i]['question'] = PARSER.convert(d.get('question')).strip().replace('<p>', '').replace('</p>', '')
                for ii, a in enumerate(d['answers']['correct']):
                    evaluation[i]['answers']['correct'][ii] = PARSER.convert(a).strip().replace('<p>', '').replace('</p>', '')
                for ii, a in enumerate(d['answers']['incorrect']):
                    evaluation[i]['answers']['incorrect'][ii] = PARSER.convert(a).strip().replace('<p>', '').replace('</p>', '')

            soup = BeautifulSoup(html_body, 'lxml')

            # 1. Attempt to download any images
            if self.repo:
                REPO_CLEAR = self.repo.split("/")[-1]

                # Only download images if self.repo is set
                for image in soup.find_all("img"):
                    src = image.get('src')
                    if not src:
                        log.warning(f"An image with no src attribute detected in lesson: {image}")
                        continue
                    filename = image['src'].split('/')[-1]
                    url = f'https://raw.githubusercontent.com/DHRI-Curriculum/{REPO_CLEAR}/{self.branch}/images/{filename}'
                    local_file = STATIC_IMAGES['LESSONS'] / Path(REPO_CLEAR) / filename

                    if '//' in url:
                        url = url.replace('//', '/').replace('https:/', 'https://').replace('http:/', 'http://')

                    download_image(url, local_file)
                    local_url = f'/static/website/images/lessons/{REPO_CLEAR}/{filename}'
                    image['src'] = local_url
                    image['class'] = image.get('class', []) + ['img-fluid', 'd-block', 'my-4']

            # 2. Find and test links
            for link in soup.find_all("a"):
                href = link.get('href')

                if not href:
                    log.warning(f"A link with no `href` attribute detected in lesson: {link}")
                    continue

                if "github.com/DHRI-Curriculum" in href:
                    # internal link found
                    if 'https://github.com/DHRI-Curriculum/' in href:
                        OUTBOUND_CLEAR = "".join(href.split("https://github.com/DHRI-Curriculum/")[1:])
                    elif 'https://www.github.com/DHRI-Curriculum/' in href:
                        OUTBOUND_CLEAR = "".join(href.split("https://www.github.com/DHRI-Curriculum/")[1:])
                    elif 'http://github.com/DHRI-Curriculum/' in href:
                        OUTBOUND_CLEAR = "".join(href.split("http://github.com/DHRI-Curriculum/")[1:])
                    elif 'http://www.github.com/DHRI-Curriculum/' in href:
                        OUTBOUND_CLEAR = "".join(href.split("http://www.github.com/DHRI-Curriculum/")[1:])
                    if OUTBOUND_CLEAR.strip() == '': OUTBOUND_CLEAR = href

                    if 'raw=true' in OUTBOUND_CLEAR.lower() or '/raw/' in OUTBOUND_CLEAR.lower() or 'raw.githubusercontent.com' in href.lower():
                        c = WebCache(href)
                        link['target'] = '_blank'
                    elif 'raw=true' not in OUTBOUND_CLEAR.lower() and '/raw/' not in OUTBOUND_CLEAR.lower() and OUTBOUND_CLEAR.lower().startswith(REPO_CLEAR.lower()):
                        log.warning(f"The lesson `{title}` links to the workshop on GitHub rather than the curriculum site: {href}")
                    else:
                        workshop = OUTBOUND_CLEAR.split('/')[0]

                        if workshop == 'install':
                            slug = OUTBOUND_CLEAR.split('/')[-1].split('.md')[0]
                            s = search_software(slug)
                            link_url = None
                            if s:
                                for software in s:
                                    for i in software.instructions.all():
                                        if not i.slug:
                                            print(i, 'has no slug!!!')
                                            continue
                                        url = reverse('install:installation', args=[i.slug])
                                        if not link_url: link_url = url
                                link['href'] = link_url
                                log.info(f"Found a link to an installation instruction for a software that was found in the site's installation instructions ({slug}). Added link to {link_url}.")
                            else:
                                log.warning(f"Found a link to an installation instruction for a software that cannot be found in the site's installation instructions ({slug}). Will add link to general installation instead. You may want to add this installation instruction to the /install/ repo on GitHub.")
                                link['href'] = reverse('install:index')

                        elif workshop == 'insights':
                            slug = OUTBOUND_CLEAR.split('/')[-1].split('.md')[0]
                            s = search_insight(slug)
                            if s:
                                if s.count() > 1:
                                    s = s.last()
                                    url = reverse('insight:insight', args=[s.slug])
                                    link['href'] = url
                                    log.warning(f"Found a link to an insight that corresponded to more than one insight on the site ({slug}). Linking to the most recent ({url})...")
                                elif s.count() == 1:
                                    s = s.last()
                                    url = reverse('insight:insight', args=[s.slug])
                                    link['href'] = url
                                    log.log(f'Found a link to an insight that corresponded to an existing insight on the site. Adding...')
                                else:
                                    link['href'] = reverse('insight:index')
                                    log.warning(f"Could not interpret result when searching for an insight on the site ({slug}). Result generated was: {s}. Will add link to general insights instead. You may want to add this term to the /insight/ repo on GitHub.")
                            else:
                                link['href'] = reverse('insight:index')
                                log.warning(f"Could not find an insight on the site ({slug}). Result generated was: {s}. Will add link to general insights instead. You may want to add this term to the /insight/ repo on GitHub.")

                        elif workshop == 'glossary':
                            slug = OUTBOUND_CLEAR.split('/')[-1].split('.md')[0]
                            s = search_term(slug)
                            if s:
                                if s.count() > 1:
                                    s = s.last()
                                    url = reverse('glossary:term', args=[s.slug])
                                    link['href'] = url
                                    log.warning(f"Found a link that corresponded to more than one term in the glossary ({slug}). Linking to the most recent ({url})...")
                                elif s.count() == 1:
                                    s = s.last()
                                    url = reverse('glossary:term', args=[s.slug])
                                    link['href'] = url
                                    log.info(f'Found a link to the glossary that corresponded to a term existing on the site. Adding...')
                                else:
                                    link['href'] = reverse('glossary:index')
                                    log.warning(f"Could not interpret result when searching for a term in the site's glossary ({slug}). Result generated was: {s}. Will add link to general glossary instead. You may want to add this term to the /glossary/ repo on GitHub.")
                            else:
                                link['href'] = reverse('glossary:index')
                                log.warning(f"Found a link to a term that cannot be found in the site's glossary ({slug}). Will add link to general glossary instead. You may want to add this term to the /glossary/ repo on GitHub.")

                        else:
                            log.warning(f"The lesson `{title}` links to other workshop/root curriculum: {REPO_CLEAR} —> {OUTBOUND_CLEAR}")
                elif href.startswith('mailto:'):
                    # email link found
                    log.warning(f"A link was inserted into lesson `{title}` with a mailto-link: {link}")
                elif href.startswith('http') or href.startswith('//'):
                    # external link found
                    c = WebCache(href)
                    link['target'] = '_blank'
                elif 'lessons.md#' in href.lower() or (href.startswith('#') and link.text):
                    # relative link found
                    log.warning(f"The lesson `{title}` contains a relative href ({href}) which may or may not work in production. Change links in the repository's `lessons.md` file on GitHub to include absolute links.")
                elif href.startswith('#') and not link.text:
                    # GitHub placeholder link found
                    pass
                else:
                    g = re.search(r'(\d+).*(md)', href)
                    if g:
                        order = int(g.groups()[0])
                        link['href'] = f'?page={order}'
                        log.warning(f"The lesson `{title}` links to an internal file `{href}` and has been relinked to `?page={order}` instead. You may want to change this manually, in case the pages do not match any longer.")
                    else:
                        if ".png" in href or ".jpg" in href or ".jpeg" in href or ".gif" in href:
                            filename = href.split('/')[-1]
                            local_url = f'/static/website/images/lessons/{REPO_CLEAR}/{filename}'
                            link['href'] = local_url
                            log.info(f"The lesson `{title}` links to an image and has been rerouted: {href} —> {local_url})")
                        else:
                            log.warning(f"The lesson `{title}` links to an internal file: {href} (** could not be deciphered)")

            # 3. Fix tables
            scrollable_div = BeautifulSoup('<div class="scrollable">', 'lxml').div
            for table in soup.find_all("table"):
                table.wrap(scrollable_div)
                table['class'] = table.get('class', []) + ['table']

            for tr in soup.find_all("tr"):
                tr['height'] = 'auto'

            # 4. Replace transpositions
            string_soup = "".join([str(x) for x in soup.body.children])
            for transposition in LESSON_TRANSPOSITIONS:
                if (string_soup.find(transposition + '<br>'),
                    string_soup.find(transposition + '<br/>'),
                    string_soup.find(transposition + '<br />')):
                    string_soup = string_soup.replace(transposition + '<br>', transposition).replace(transposition + '<br/>', transposition).replace(transposition + '<br />', transposition)
                string_soup = string_soup.replace(transposition, LESSON_TRANSPOSITIONS[transposition])

            # 5. Replace body with string_soup, after cleaning it up
            html_body = string_soup

            # 6. Clean up any challenge and solution data (insert any such edits here)
            html_challenge = html_challenge
            html_solution = html_solution

            html_data = {
                    'title': title,
                    'text': html_body,
                    'challenge': html_challenge,
                    'challenge_title': challenge_title,
                    'solution': html_solution,
                    'solution_title': solution_title,
                    'evaluation': evaluation,
                    'keywords': keywords,
                }

            self.html_data.append(html_data)


    def __len__(self):
        return(len(self.data))


class GlossaryCache():

    log = Logger(name='glossary-loader-cache')

    def __init__(self, loader, force_download=FORCE_DOWNLOAD):
        self.loader = loader

        self.path = CACHE_DIRS['ROOT'] / (self.loader.repo_name + ".json")
        self.expired = _is_expired(self.path, age_checker=TEST_AGES["GLOSSARY"], force_download=force_download) == True

        new_content = False
        if not self.path.exists():
            log.warning(f'{self.path} does not exist so downloading glossary cache...')
            self._setup_raw_content()
            new_content = True

        if new_content == False and (force_download == True or self.expired == True):
            if force_download == True:
                log.warning(f'Force download is set to True or cache file has expired so downloading glossary cache...')
            self._setup_raw_content()

        self.data = self.load()


    def _setup_raw_content(self):
        self.data = {
            'terms_raw': self._load_raw_text()
        }
        self.save()


    def _load_raw_text(self):
        log.log(f'Loading raw text from {self.loader.repo_name}...')

        r = requests.get(f'https://github.com/DHRI-Curriculum/{self.loader.repo_name}/tree/{self.loader.branch}/terms')

        soup = BeautifulSoup(r.text, 'lxml')

        results = dict()

        for _ in soup.find_all("div", {"class": "js-navigation-item"})[1:]:
            link = _.find('a')['href']
            filename = link.split('/')[-1]
            term = ".".join(filename.split('.')[:-1])

            log.log(f'Loading raw text from term `{term}`...')
            raw_url = f'https://raw.githubusercontent.com/DHRI-Curriculum/{self.loader.repo_name}/{self.loader.branch}/terms/{filename}'
            r = requests.get(raw_url)
            results[term] = r.text

        return(results)


    def save(self):
        """Saves <self.data> into <self.path>"""
        if not self.path.parent.exists(): self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps(self.data))


    def load(self):
        """Loads <self.data> from <self.path>"""
        return json.loads(self.path.read_text())




from backend.dhri_settings import GLOSSARY_REPO

class GlossaryParser():
    readings = list()
    tutorials = list()
    explication, readings_md, tutorials_md = None, None, None
    log = Logger('glossary-parser')

    def __init__(self, data:str):
        self.data = data
        self.term = list(split_into_sections(data, level_granularity=1).keys())[0].strip()
        for header, md in split_into_sections(data, level_granularity=2).items():
            if header == self.term:
                self.explication = md
            elif header == 'Readings' or (header == 'Reading' and self.readings_md == None):
                self.readings_md = md
            elif header == 'Tutorials' or (header == 'Tutorial' and self.tutorials_md == None):
                self.tutorials_md = md
            else:
                self.log.error(f'Unable to parse {header} in term {self.term}.')

        if self.readings_md:
            self.readings = as_list(self.readings_md)

        if self.tutorials_md:
            self.tutorials = as_list(self.tutorials_md)

        if self.explication:
            self.explication = PARSER.convert(self.explication)

        self._tutorials = list()
        for tutorial in self.tutorials:
            annotation = PARSER.convert(tutorial)
            linked_text, url = extract_links(tutorial)[0] # TODO: Only extracting one link here...
            self._tutorials.append({
                'annotation': annotation,
                'linked_text': linked_text,
                'url': url
            })
        self.tutorials = self._tutorials

        self._readings = list()
        for reading in self.readings:
            annotation = PARSER.convert(reading)
            linked_text, url = extract_links(reading)[0] # TODO: Only extracting one link here...
            self._readings.append({
                'annotation': annotation,
                'linked_text': linked_text,
                'url': url
            })
        self.readings = self._readings

class GlossaryLoader():

    log = Logger(name='glossary-loader')
    terms = dict()
    all_terms = list()

    def __init__(self, glossary_repo=GLOSSARY_REPO, force_download=FORCE_DOWNLOAD):
        self.repo_name = glossary_repo[0]
        self.branch = glossary_repo[1]

        self.data = GlossaryCache(self, force_download=force_download).data

        # Map properties
        self.terms_raw = self.data.get('terms_raw')

        for term, data in self.terms_raw.items():
            self.terms[term] = GlossaryParser(data)
            self.all_terms.append(term)