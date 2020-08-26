"""Loader functionality for DHRI Curriculum"""


import datetime
import json
import requests
import re

from pathlib import Path
from bs4 import BeautifulSoup, Comment
from requests.exceptions import HTTPError, MissingSchema

from backend.models import *

from backend.dhri.exceptions import MissingCurriculumFile, MissingRequiredSection
from backend.dhri.log import Logger, get_or_default
from backend.dhri.markdown import split_into_sections, as_list, extract_links
from backend.dhri.markdown_parser import PARSER
from backend.dhri.text import get_number
from backend.dhri.webcache import WebCache

from backend.dhri_settings import NORMALIZING_SECTIONS, FORCE_DOWNLOAD, BACKEND_AUTO, \
                                    REPO_AUTO, BRANCH_AUTO, TEST_AGES, CACHE_DIRS, \
                                    STATIC_IMAGES, LESSON_TRANSPOSITIONS


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
        'discussion_questions': (Praxis, False),
        'next_steps': (Praxis, False),
        'tutorials': (Tutorial, False),
        'further_readings': (Reading, False),
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

    log.log(f'Cache is OK for {path} - not older than {age_checker}....')
    return False


def process_links(input, obj):
    """<#TODO: doctstr>"""
    links = extract_links(input)
    if links:
        title, url = links[0]
    else:
        return(None, None)
    if len(links) > 1:
        log.warning(f'One project seems to contain more than one URL, but only one ({url}) is captured: {links}')
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

    # TODO: Include _assessment_sections test here?


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
        self.frontmatter['learning_objectives'] = [str(_) for _ in as_list(self.frontmatter.get('learning_objectives'))]
        self.frontmatter['ethical_considerations'] = [str(_) for _ in as_list(self.frontmatter.get('ethical_considerations'))]

        # fix praxis data sections
        self.praxis['discussion_questions'] = [str(_) for _ in as_list(self.praxis.get('discussion_questions'))]
        self.praxis['next_steps'] = [str(_) for _ in as_list(self.praxis.get('next_steps'))]
        self.praxis['tutorials'] = [str(_) for _ in as_list(self.praxis.get('tutorials'))]
        self.praxis['further_readings'] = [str(_) for _ in as_list(self.praxis.get('further_readings'))]

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

        self._test_for_files()

        # Mapping frontmatter sections
        self.abstract = self.frontmatter.get('abstract')
        self.estimated_time = self.frontmatter.get('estimated_time')
        self.contributors = self.frontmatter.get('contributors')
        self.readings = self.frontmatter.get('readings')
        self.projects = self.frontmatter.get('readings')
        self.learning_objectives = self.frontmatter.get('learning_objectives')
        self.ethical_considerations = self.frontmatter.get('ethical_considerations')

        # Mapping praxis sections
        self.discussion_questions = self.praxis.get('discussion_questions')
        self.next_steps = self.praxis.get('next_steps')
        self.tutorials = self.praxis.get('tutorials')
        self.further_readings = self.praxis.get('further_readings')


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
                first_name, last_name = self.split_names(name)
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
                log.warning(f"Could not download image {local_file.name} (not found): {url}")
                return None
            elif r.status_code == 403:
                log.warning(f"Could not download image {local_file.name} (not allowed)")
                return None
        elif r.status_code == 403:
            log.warning(f"Could not download image {local_file.name} (not allowed)")
            return None
    else:
        return local_file


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

        for title, body in split_into_sections(self.markdown, level_granularity=1, clear_empty_lines=False).items():
            droplines = []

            challenge = ""
            # 1. Test markdown for challenge
            if "## challenge" in body.lower() or "## activity" in body.lower():
                for line_num, line in enumerate(body.splitlines()):
                    if line.lower().startswith("## challenge") or line.lower().startswith("## activity"):
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

            solution = ""
            # 2. Test markdown for solution
            if "solution" in body.lower():
                for line_num, line in enumerate(body.splitlines()):
                    if line.lower().startswith("## solution"):
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

            # 3. Fix markdown body
            cleaned_body = ''
            for i, line in enumerate(body.splitlines()):
                if line.strip() == '': continue
                if i not in droplines:
                    cleaned_body += line + '\n'
            
            cleaned_body = re.sub(r' +', ' ', cleaned_body)
            cleaned_body = re.sub(r'\n+', '\n', cleaned_body)

            # 4. Clean up all markdown data
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
                log.warning(f'The lesson `{title}` has a challenge with no solution.')

            data = {
                    'title': title,
                    'text': cleaned_body,
                    'challenge': challenge,
                    'solution': solution
                }

            self.data.append(data)


            # Next up: HTML parsing

            html_body = PARSER.convert(cleaned_body)
            html_challenge, html_solution = '', ''

            if challenge:
                html_challenge = PARSER.convert(challenge)

            if solution:
                html_solution = PARSER.convert(solution)

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
                    image['class'] = image.get('class', []) + ['img-fluid']

            # 2. Find and test links
            for link in soup.find_all("a"):
                href = link.get('href')
                if not href:
                    log.warning(f"A link with no href attribute detected in lesson: {link}")
                    continue
                if "github.com/DHRI-Curriculum" in href:
                    OUTBOUND_CLEAR = "".join(href.split("https://github.com/DHRI-Curriculum/")[1:])
                    if OUTBOUND_CLEAR.strip() == '': OUTBOUND_CLEAR = href
                    if OUTBOUND_CLEAR.startswith(REPO_CLEAR):
                        log.warning(f"The lesson `{title}` links to same workshop: {href}")
                    else:
                        log.warning(f"The lesson `{title}` links to other workshop/root curriculum: {REPO_CLEAR} —> {OUTBOUND_CLEAR}")
                elif href.startswith('http') or href.startswith('//'):
                    c = WebCache(href)
                elif href.startswith('#'):
                    log.log(f"The lesson `{title}` contains a relative href ({href}) which may or may not work in production.", color="yellow")
                else:
                    g = re.search(r'(\d+).*(md)', href)
                    if g:
                        order = int(g.groups()[0])
                        link['href'] = f'?page={order}'
                        log.log(f"The lesson `{title}` links to an internal file `{href}` and has been relinked to `?page={order}` instead.", color="yellow")
                    else:
                        if ".png" in href or ".jpg" in href or ".gif" in href:
                            filename = href.split('/')[-1]
                            local_url = f'/static/website/images/lessons/{REPO_CLEAR}/{filename}'
                            link['href'] = local_url
                            log.log(f"The lesson `{title}` links to an image and has been rerouted: {href} —> {local_url})", color='yellow')
                        else:
                            log.warning(f"The lesson `{title}` links to an internal file: {href} (** could not be deciphered)")

            # 3. Fix tables
            for table in soup.find_all("table"):
                table['class'] = table.get('class', []) + ['table']

            for tr in soup.find_all("tr"):
                tr['height'] = 'auto'

            # 4. Replace transpositions
            string_soup = str(soup)
            for transposition in LESSON_TRANSPOSITIONS:
                if (string_soup.find(transposition + '<br>'),
                    string_soup.find(transposition + '<br/>'),
                    string_soup.find(transposition + '<br />')):
                    string_soup = string_soup.replace(transposition + '<br>', transposition).replace(transposition + '<br/>', transposition).replace(transposition + '<br />', transposition)
                string_soup = string_soup.replace(transposition, LESSON_TRANSPOSITIONS[transposition])

            # 5. Replace body with string_soup, after cleaning it up
            html_body = string_soup
                # .replace('<html><body>', '').replace('</body></html>', '').replace('\n<br />\n', '').replace('\n<br />\n', '').replace('<br />', '</p><p>').replace('<br/>', '</p><p>').replace('<br>', '</p><p>')

            # 6. Clean up any challenge and solution data
            html_challenge = html_challenge
                #.replace('\n<br />\n', '').replace('\n<br />\n', '').replace('<br />', '</p><p>').replace('<br/>', '</p><p>').replace('<br>', '</p><p>')
            html_solution = html_solution
                #.replace('\n<br />\n', '').replace('\n<br />\n', '').replace('<br />', '</p><p>').replace('<br/>', '</p><p>').replace('<br>', '</p><p>')

            html_data = {
                    'title': title,
                    'text': html_body,
                    'challenge': html_challenge,
                    'solution': html_solution
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

        if not self.path.exists():
            log.warning(f'{self.path} does not exist so downloading glossary cache...')
            self._setup_raw_content()

        if force_download == True:
            log.warning(f'Force download is set to True so downloading glossary cache...')
            self._setup_raw_content()

        if self.expired == True:
            log.warning(f'File is expired (set to {self.expired}) so downloading glossary cache...')
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

    def __init__(self, data:str):
        self.data = data
        self.term = list(split_into_sections(data, level_granularity=1).keys())[0]
        for header, md in split_into_sections(data, level_granularity=2).items():
            if header == self.term:
                self.explication = md
            elif header == 'Readings' or (header == 'Reading' and self.readings_md == None):
                self.readings_md = md
            elif header == 'Tutorials' or (header == 'Tutorial' and self.tutorials_md == None):
                self.tutorials_md = md
            else:
                print(f'Error: Unable to parse {header} in term {self.term}.')

        if self.readings_md:
            self.readings = as_list(self.readings_md)

        if self.tutorials_md:
            self.tutorials = as_list(self.tutorials_md)

        if self.explication:
            self.explication = PARSER.convert(self.explication)

        self._tutorials = list()
        for i, tutorial in enumerate(self.tutorials):
            annotation = PARSER.convert(tutorial)
            linked_text, url = extract_links(tutorial)[0] # TODO: Only extracting one link here...
            self._tutorials.append({
                'annotation': annotation,
                'linked_text': linked_text,
                'url': url
            })
        self.tutorials = self._tutorials

        self._readings = list()
        for i, reading in enumerate(self.readings):
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