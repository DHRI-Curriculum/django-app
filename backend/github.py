'''
This library is used for the `build` commands related to the DHRI Curriculum
'''

import git
import os
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from nameparser import HumanName

from backend.settings import CACHE_DIRS, IMAGE_CACHE, NORMALIZING_SECTIONS, BACKEND_AUTO
from backend.markdown_parser import PARSER
from backend.dhri_utils import extract_links, split_into_sections, as_list, get_terminal_width
from backend.mixins import convert_html_quotes


class MarkdownError(Exception):
    pass


class Helper():
    IMAGE_REGEX = re.compile(r'(?:!\[(.*?)\]\((.*?)\))')

    def _extract_from_p(self, html):
        return ''.join([str(x) for x in BeautifulSoup(html, 'lxml').p.children])

    def _get_image_from_first_line(self, markdown=''):
        if markdown == '' or markdown == None:
            return '', ''
        if markdown.splitlines()[0].startswith('!['):
            image = markdown.splitlines()[0]
            finder = self.IMAGE_REGEX.search(markdown)
            if finder:
                return {'alt': finder.groups()[0], 'url': finder.groups()[1]}
            else:
                raise MarkdownError(f'Found image but likely misformatted. Try to correct this markdown: `{image}`') from None
        return {'alt': '', 'url': ''}

    @staticmethod
    def _fix_list_element(markdown):
        html = WorkshopCache.HTML_parser(markdown)
        soup = BeautifulSoup(html, 'lxml')
        link = soup.find('a')
        text, url = None, None
        if link:
            url = link['href']
            text = link.text
        _ = {
            'annotation': convert_html_quotes(''.join([str(x) for x in soup.p.children])),
            'linked_text': convert_html_quotes(text),
            'url': url
        }
        return _

    @staticmethod
    def _get_order(step, log=None):
        g = re.search(r"Step ([0-9]+): ", step)
        if g:
            order = g.groups()[0]
            step = re.sub(r'Step ([0-9]+): ', '', step)
            try:
                step = int(step)
            except:
                pass
        else:
            order = 0
            raise MarkdownError(
                'Found an installation step that does not show the order clearly (see documentation). Cannot determine order: ' + str(step)) from None
        return(order, step)

    @staticmethod
    def download_image(url, local_file):
        if not isinstance(local_file, Path):
            local_file = Path(local_file)
        if not local_file.parent.exists():
            local_file.parent.mkdir(parents=True)
        if not local_file.exists():
            r = requests.get(url)
            if r.status_code == 200:
                with open(local_file, 'wb+') as f:
                    for chunk in r:
                        f.write(chunk)
                return True
            elif r.status_code == 404:
                url = url.replace('/images/', '/sections/images/')
                r = requests.get(url)
                if r.status_code == 200:
                    with open(local_file, 'wb+') as f:
                        for chunk in r:
                            f.write(chunk)
                    return True
                elif r.status_code == 404:
                    exit(
                        f"Could not download image {local_file.name} (not found): {url}")
                elif r.status_code == 403:
                    exit(
                        f"Could not download image {local_file.name} (not allowed)")
            elif r.status_code == 403:
                exit(
                    f"Could not download image {local_file.name} (not allowed)")
        else:
            return True

    '''
    @staticmethod
    def process_links(input, obj, is_html=False, allow_no_link=True) -> tuple:
        """<TODO: docstr>"""
        title, url, links = None, None, []
        if is_html == False:
            links = extract_links(input)
            if links:
                title, url = links[0]
            else:
                return(None, None, [])
        elif is_html:
            soup = BeautifulSoup(input, 'lxml')
            links = soup.find_all('a')
            if len(links) == 0 and allow_no_link:
                return(None, None, [])
            elif len(links) == 0 and allow_no_link == False:
                raise MarkdownError(
                    f'A link was expected in the input but could not be parsed: `{input}`') from None
            title, url = links[0].text, links[0]['href']

        if title == None or title == '':
            from backend.webcache import WebCache
            from backend.logger import get_or_default
            title = WebCache(url).title
            title = get_or_default(
                f'Set a title for the {obj} at {url}: ', title)  # import..?

        return(title, url, links)
    '''

    @staticmethod
    def process_prereq_text(html, log=None):
        soup = BeautifulSoup(html, 'lxml')

        captured_link = False
        for node in soup.body.children:
            is_link = node.name.lower() == 'a'
            if is_link and not captured_link:
                captured_link = node['href']
                node.decompose()
            elif is_link and captured_link:
                log.info(f'More than one link in prerequirement. Try to keep the number of links for each prerequirement to one as it may otherwise be confusing.')
        text = ''.join([x for x in soup.body.children])
        text = text.strip()
        text = text.replace('(recommended) ', '').replace('(required) ', '')

        if text == '':
            text = None

        return text


class GitCache():
    backend = BACKEND_AUTO
    repository = ''
    branch = ''
    CACHE_DIRS = CACHE_DIRS
    cache_dir = ''
    destination_dir = ''
    repo = None
    HTML_parser = PARSER.convert
    parsed_data = {}

    def __init__(self, repository=None, branch=None, cache_dir=None, destination_dir=None, log=None):
        self.repository = repository
        self.branch = branch
        self.cache_dir = cache_dir
        self.log = log
        if destination_dir == None:
            self.destination_dir = self.CACHE_DIRS[self.cache_dir]
        else:
            self.destination_dir = destination_dir
        
        self.reset()
        if not os.path.exists(self.destination_dir):
            self.log.log(f'Repository directory does not exist so cloning: {self.destination_dir}')
            self.repo = self._clone()
        else:
            self.log.log(f'Repository directory exists so creating connection to repository: {self.destination_dir}')
            self.repo = git.Repo(self.destination_dir)
            self.log.log(f'Pulling latest repository updates from remotes origin...')
            self.repo.remotes.origin.pull()

        self.log.log(f'Ensuring repository has correct branch checked out: {self.branch} ({self.repository})')
        self.repo.git.checkout(self.branch, force=True)

    def _clone(self):
        if self.backend.lower() == 'github':
            url = f'http://www.github.com/DHRI-Curriculum/{self.repository}'
            self.log.log(f'Cloning repository from GitHub: {url}')
            self.repo = git.Repo.clone_from(url, self.destination_dir)
        else:
            raise NotImplementedError(
                f'Backend `{self.backend}` cannot be used. No implementation for it.')
        return self.repo

    @property
    def files(self, directory=None, include_invisible=False):
        if not directory:
            directory = self.destination_dir
        if include_invisible:
            return [x for x in os.listdir(self.destination_dir) if not os.path.isdir(os.path.join(self.destination_dir, x))]
        return [x for x in os.listdir(self.destination_dir) if not os.path.isdir(os.path.join(self.destination_dir, x)) and not x.startswith('.')]

    @property
    def directories(self, directory=None, include_invisible=False):
        if not directory:
            directory = self.destination_dir
        if include_invisible:
            return [x for x in os.listdir(directory) if os.path.isdir(os.path.join(directory, x))]
        return [x for x in os.listdir(directory) if os.path.isdir(os.path.join(directory, x)) and not x.startswith('.')]

    def contents_of(self, directory=''):
        if directory in self.directories:
            return [x for x in os.listdir(os.path.join(self.destination_dir, directory)) if not x.startswith('.')]

    def reset(self):
        if os.path.exists(self.destination_dir):
            import shutil
            shutil.rmtree(self.destination_dir)

    def read_file(self, path):
        with open(path, 'r') as f:
            return f.read()

    @classmethod
    def get_stem(self, path):
        return os.path.basename(path).split('.')[0]

    @property
    def data(self):
        if not self.parsed_data:
            try:
                self.parsed_data = self.parse()
            except AttributeError as e:
                if 'has no attribute' in str(e) and 'parse' in str(e):
                    raise AttributeError(
                        f'The class needs a parse method.') from None
        return self.parsed_data


class GlossaryCache(Helper, GitCache):

    def __init__(self, repository='glossary', branch='v2.0', log=None):
        self.repository = repository
        self.branch = branch
        self.cache_dir = 'GLOSSARY'
        self.log = log
        super().__init__(repository=self.repository,
                         branch=self.branch, cache_dir=self.cache_dir, log=log)

    def parse(self):
        terms = []
        for file in self.contents_of('terms'):
            try:
                file_contents = self.read_file(
                    os.path.join(self.destination_dir, 'terms', file))
            except FileNotFoundError:
                raise FileNotFoundError(
                    f'Warning: File {file} could not be found. Run ._clone()')

            _ = {
                'term': None,
                'explication': None,
                'readings': None,
                'tutorials': None
            }
            sections = split_into_sections(file_contents)
            for section in sections:
                if section == 'Readings':
                    _['readings'] = [self._fix_list_element(x) for x in as_list(sections[section])]
                elif section == 'Tutorials':
                    _['tutorials'] = [self._fix_list_element(x) for x in as_list(sections[section])]
                else:
                    _['term'] = section
                    _['explication'] = convert_html_quotes(self.HTML_parser(sections[section]))
            terms.append(_)
        return terms


class InstallCache(Helper, GitCache):

    def __init__(self, repository='install', branch='v2.0', log=None):
        self.cache_dir = 'INSTALL'
        self.repository = repository
        self.branch = branch
        self.log = log
        super().__init__(repository=self.repository,
                         branch=self.branch, cache_dir=self.cache_dir, log=log)
        self.image_baseurl = f'https://raw.githubusercontent.com/DHRI-Curriculum/{self.repository}/{self.branch}/guides/images/' # needs to end with /
        
    def parse(self):
        instructions = []
        for file in self.contents_of('guides'):
            try:
                file_contents = self.read_file(os.path.join(
                    self.destination_dir, 'guides', file))
            except FileNotFoundError:
                raise FileNotFoundError(
                    f'Warning: File {file} could not be found. Run ._clone()')
            except IsADirectoryError:
                continue

            _ = {
                'image': None,
                'image_alt': None,
                'software': None,
                'what': None,
                'why': None,
                'instructions': {
                    'Windows': [],
                    'macOS': []
                },
                'additional_sections': {}
            }

            # Get image
            if self._get_image_from_first_line(file_contents):
                data = self._get_image_from_first_line(file_contents)
                data = self._fix_image(data)
                _['image_alt'], _['image'] = data['alt'], data['url']
                
                file_contents = '\n'.join(file_contents.splitlines()[1:])

            # Get `software`
            sections = split_into_sections(file_contents, level_granularity=1)
            if len(sections) == 1:
                _['software'] = list(sections.keys())[0]
            else:
                raise MarkdownError(f'The file {file} does not appear to contain a level 1 header, and parser could not find a title')
            
            i = 0
            # Get all sections
            for section, content in split_into_sections(file_contents, level_granularity=2).items():
                if section == _['software'] or content == '':
                    continue
                if 'what it is' in section.lower():
                    _['what'] = convert_html_quotes(self.HTML_parser(content.replace('---', '')))
                elif 'why we use it' in section.lower():
                    _['why'] = convert_html_quotes(self.HTML_parser(content.replace('---', '')))
                elif 'installation instructions' in section.lower():
                    if 'mac' in section.lower():
                        _['instructions']['macOS'] = []
                        content = split_into_sections(content)
                        for section, content in content.items():
                            __ = {}
                            __['step'], __['header'] = self._get_order(section)
                            #__['text'] = self.HTML_parser(content)
                            __['html'], __['screenshots'] = self._get_screenshots_from_markdown(content, relative_dir='guides')
                            __['html'] = convert_html_quotes(__['html'])
                            _['instructions']['macOS'].append(__)
                    elif 'windows' in section.lower():
                        _['instructions']['Windows'] = []
                        content = split_into_sections(content)
                        for section, content in content.items():
                            __ = {}
                            __['step'], __[
                                'header'] = self._get_order(section)
                            #__['text'] = self.HTML_parser(content)
                            __['html'], __['screenshots'] = self._get_screenshots_from_markdown(content, relative_dir='guides')
                            __['html'] = convert_html_quotes(__['html'])
                            _['instructions']['Windows'].append(__)
                else:
                    if not section in _['additional_sections']:
                        i += 1
                        _['additional_sections'][section] = {
                            'content': convert_html_quotes(self.HTML_parser(content)),
                            'order': i
                        }
                    else:
                        raise MarkdownError(
                            f'Multiple sections with the same header found in the installation instructions for {_["software"]}: `{section}`. Please correct before running script again.')

            instructions.append(_)
        
        return instructions

    def _fix_image(self, dictionary):
        url = dictionary.get('url').replace('https://', '').replace('http://', '').replace(
            f'raw.githubusercontent.com/DHRI-Curriculum/{self.repository}/{self.branch}/', '')
        parents = [x for x in url.split('/') if not '.' in x]
        local_file = self.destination_dir
        for _dir in parents:
            local_file = os.path.join(local_file, _dir)
        local_file += '/' + os.path.basename(url).replace('%40', '@')
        if os.path.exists(local_file):
            return {'url': local_file, 'alt': dictionary.get('alt')}
        else:
            exit('error! fix this!') # TODO: Fix this...
            return {'url': url, 'alt': dictionary.get('alt')}

    def _get_screenshots_from_markdown(self, markdown='', relative_dir=None):
        screenshots = []

        html = self.HTML_parser(markdown)
        soup = BeautifulSoup(html, 'lxml')
        for img_data in soup.find_all('img'):
            img = {}
            img['alt'] = img_data.get('alt')
            img['src'] = img_data.get('src')
            if not img['src']:
                self.log.warning(
                    f"An image with no src attribute detected in installation instruction step: {img}. Skipping...")
                continue

            if img['src'].startswith('/'):
                # we have an absolute image, so we should be able to get local_image from this path
                local_image = (str(self.destination_dir) +
                               '/' + img['src']).replace('//', '/')
            else:
                # we have a relative image, so construct its entire path in the repo
                local_image = self.destination_dir
                if relative_dir:
                    local_image = os.path.join(local_image, relative_dir)
                for _dir in [x for x in img['src'].split('/') if not '.' in x]:
                    local_image = os.path.join(local_image, _dir)
                local_image += '/' + os.path.basename(img['src'])
            if os.path.exists(local_image):
                pass  # the image already exists
            else:
                filename = os.path.basename(img['src'])
                local_destination = IMAGE_CACHE['INSTALL'] / filename
                self.log.warning(
                    f'Expected local path does not exist: `{local_image}`... Downloading to temporary local storage (`{local_destination}`)!')
                url = f'{self.image_baseurl}{filename}'
                if self.download_image(url, local_destination):
                    local_image = local_destination

            if local_image:
                screenshots.append({'path': local_image, 'alt': img['alt']})
                img_data.decompose()

        for a in soup.find_all('a'):
            if a.text == '':
                a.decompose()

        html = ''.join([str(x) for x in soup.body.children])

        return html, screenshots


class InsightCache(Helper, GitCache):

    def __init__(self, repository='insights', branch='v2.0', log=None):
        self.repository = repository
        self.branch = branch
        self.cache_dir = 'INSIGHT'
        self.log = log
        super().__init__(repository=self.repository,
                         branch=self.branch, cache_dir=self.cache_dir, log=log)

    def parse(self):
        insights = []
        for file in self.contents_of('pages'):
            try:
                file_contents = self.read_file(
                    os.path.join(self.destination_dir, 'pages', file))
            except FileNotFoundError:
                raise FileNotFoundError(
                    f'Warning: File {file} could not be found. Run ._clone()')
            except IsADirectoryError:
                continue

            _ = {
                'image': self._get_image_from_first_line(file_contents),
                'insight': list(split_into_sections(file_contents, level_granularity=1).keys())[0],
                'introduction': '',
                'os_specific': {},
                'sections': {}
            }

            _['image'] = self._fix_image(_['image'])

            sections = split_into_sections(file_contents, level_granularity=2)
            order = 0
            for section, content in sections.items():
                if section == _['insight']:
                    _['introduction'] = convert_html_quotes(self.HTML_parser(content).strip())
                else:
                    order += 1
                    _['sections'][section] = {
                        'order': order,
                        'content': convert_html_quotes(self.HTML_parser(content))
                    }
                    has_os_specific_instruction = '### ' in content
                    if has_os_specific_instruction:
                        for operating_system, os_content in split_into_sections(content, level_granularity=3).items():
                            if operating_system == 'MacOS':
                                operating_system = 'macOS'
                            _['os_specific'][operating_system] = {
                                'content': convert_html_quotes(self.HTML_parser(os_content).strip()),
                                'related_section': section
                            }
            insights.append(_)
        return insights

    def _fix_image(self, dictionary):
        url = dictionary.get('url').replace('https://', '').replace('http://', '').replace(
            f'raw.githubusercontent.com/DHRI-Curriculum/{self.repository}/{self.branch}/', '')
        parents = [x for x in url.split('/') if not '.' in x]
        local_file = self.destination_dir
        if not 'pages' in parents:
            parents.insert(0, 'pages')
        for _dir in parents:
            local_file = os.path.join(local_file, _dir)
        local_file += '/' + os.path.basename(url).replace('%40', '@')
        if os.path.exists(local_file):
            return {'url': local_file, 'alt': dictionary.get('alt')}
        else:
            exit('error! fix this!')
            return {'url': url, 'alt': dictionary.get('alt')}


class WorkshopCache(Helper, GitCache):

    def __init__(self, repository='', branch='v2.0', log=None):
        self.repository = repository
        self.branch = branch
        self.cache_dir = 'WORKSHOPS'
        self.log = log
        super().__init__(repository=self.repository, branch=self.branch, cache_dir=self.cache_dir,
                         destination_dir=f'{self.CACHE_DIRS[self.cache_dir]}/{self.repository}', log=log)
        self.parse()

        # Set up quick access
        self.name = self.data['name']
        self.frontmatter = self.sections['frontmatter']
        self.praxis = self.sections['theory-to-practice']
        self.lessons = self.sections['lessons']
        self.image = self.data['image']

    def parse(self):
        data = {}
        self.raw = self._get_raw()
        data['raw'] = self.raw

        data['image'] = self._get_image_from_first_line(self.raw['image'])
        data['image'] = self._fix_image(data['image'])
        
        data['name'] = list(split_into_sections(
            self.raw['frontmatter'], level_granularity=1).keys())[0]
        self.sections = {key: split_into_sections(
            value) for key, value in self.raw.items()}
        self.sections = self._normalize_sections()
        self.sections['frontmatter'] = self._fix_frontmatter()
        self.sections['theory-to-practice'] = self._fix_praxis()
        self.sections['lessons'] = self._fix_lessons()

        return data

    def _get_raw(self):
        raw = {}
        try:
            raw['frontmatter'] = self.read_file(
                os.path.join(self.destination_dir, 'frontmatter.md'))
        except FileNotFoundError:
            raise FileNotFoundError(
                f'The workshop repository {self.repository} is not correctly set up. It needs a `frontmatter.md` file.') from None
        try:
            raw['lessons'] = self.read_file(
                os.path.join(self.destination_dir, 'lessons.md'))
        except FileNotFoundError:
            raise FileNotFoundError(
                f'The workshop repository {self.repository} is not correctly set up. It needs a `frontmatter.md` file.') from None
        try:
            raw['theory-to-practice'] = self.read_file(
                os.path.join(self.destination_dir, 'theory-to-practice.md'))
        except FileNotFoundError:
            raise FileNotFoundError(
                f'The workshop repository {self.repository} is not correctly set up. It needs a `frontmatter.md` file.') from None
        try:
            raw['image'] = self.read_file(
                os.path.join(self.destination_dir, 'image.md'))
        except FileNotFoundError:
            raise FileNotFoundError(
                f'The workshop repository {self.repository} is not correctly set up. It needs a `frontmatter.md` file.') from None

        return raw

    def _normalize_sections(self):
        if not self.sections:
            self.parse()

        sections = {}
        for file, section_data in NORMALIZING_SECTIONS.items():
            sections[file] = {}
            for normalized_section, spellings in section_data.items():
                found = False
                for sec, content in self.sections.get(file).items():
                    if found:
                        continue
                    if sec.lower() in [x.lower() for x in spellings]:
                        sections[file][normalized_section] = content
                        found = True
        
        self.sections = sections
        return self.sections

    @staticmethod
    def _fix_estimated_time(string):
        finder = re.search(r'(\d+([\.,][\d+])?)', string)
        if finder:
            return int(finder.groups()[0].split('.')[0])
        return ''

    @staticmethod
    def _fix_contributor(string):
        def get_correct_role(string):
            if 'author' in string.lower() or 'contributor' in string.lower():
                return 'Au'
            if 'review' in string.lower():
                return 'Re'
            if 'editor' in string.lower():
                return 'Ed'

        def split_names(full_name: str) -> tuple:
            """Uses the `nameparser` library to interpret names."""
            name = HumanName(full_name)
            first_name = name.first
            if name.middle:
                first_name += " " + name.middle
            last_name = name.last
            return((first_name, last_name))

        soup = BeautifulSoup(PARSER.convert(string), 'lxml')
        link = soup.find('a')['href']
        current = 'current' in string.lower()
        past = 'past' in string.lower()
        full_name, first_name, last_name = None, None, None
        try:
            full_name = soup.text.split(':')[1].strip()
        except IndexError:
            pass

        if full_name:
            first_name, last_name = split_names(full_name)

        return {
            'full_name': full_name,
            'first_name': first_name,
            'last_name': last_name,
            'role': get_correct_role(string),
            'current': current,
            'past': past,
            'link': link
        }

    @staticmethod
    def _warning_too_many_links(category, links, url, log):
        if len(links) > 1:
            try:
                url_list = [x['href'] for x in links]
                url_list[0] = f'*** {url}'
                link_list = '- ' + \
                    "\n    - ".join([x[:get_terminal_width()-30]
                                     for x in url_list])
            except:
                try:
                    links = [x[1] for x in links]
                    links[0] = '*** '+links[0]
                    link_list = '- ' + \
                        "\n    - ".join([x[:get_terminal_width()-30]
                                         for x in links])
                except:
                    link_list = ''
            log.info(
                f'One `{category}` seems to contain more than one URL, but only the first is captured:' + link_list)

    def _fix_frontmatter(self):
        fixing = self.sections['frontmatter']

        # Fix estimated_time
        fixing['estimated_time'] = self._fix_estimated_time(
            fixing['estimated_time'])

        fixing['abstract'] = convert_html_quotes(fixing['abstract'])

        # Make lists correct
        for _list in ['readings', 'projects', 'learning_objectives', 'ethical_considerations', 'prerequisites']:
            if _list in fixing:
                fixing[_list] = [self._fix_list_element(x) for x in as_list(fixing[_list])]
            else:
                fixing[_list] = []

        # Fixing contributors
        fixing['contributors'] = [self._fix_contributor(x) for x in as_list(fixing['contributors'])]
        
        # Fixing prerequisites
        _ = []
        for prerequisite_data in fixing['prerequisites']:
            text = None
            url = prerequisite_data.get('url')
            url_text = prerequisite_data.get('linked_text')
            html = prerequisite_data.get('annotation')
            install_link = 'github.com/DHRI-Curriculum/install/' in url
            insight_link = 'github.com/DHRI-Curriculum/insights/' in url
            workshop_link = 'github.com/DHRI-Curriculum/' in url and not '/blob/' in url
            if install_link or insight_link or workshop_link:
                text = self.process_prereq_text(html, log=self.log)
            if install_link and not text:
                self.log.warning(f'No clarifying text was found when processing prerequired installation (`{url_text}`) for workshop `{self.name}`. Note that the clarifying text will be replaced by the "why" text from the installation instructions. You may want to change this in the frontmatter\'s requirements for the workshop {self.name} and re-run `buildworkshop --name {self.repository}')
            if insight_link and not text:
                self.log.warning(f'No clarifying text was found when processing prerequired insight (`{url_text}`) for workshop `{self.name}`. Note that the clarifying text will be replaced by the default text presenting the insight. You may want to change this in the frontmatter\'s requirements for the workshop {self.name} and re-run `buildworkshop --name {self.repository}')
            if workshop_link and not text:
                self.log.warning(f'No clarifying text was found when processing prerequired workshop (`{url_text}`) for workshop `{self.name}`. Note that the clarifying text will not be replaced by any default text and can thus be confusing to the user. You may want to change this in the frontmatter\'s requirements for the workshop {self.name} and re-run `buildworkshop --name {self.repository}')

            if install_link:
                _.append({
                    'type': 'install',
                    'potential_name': self._extract_from_p(url_text),
                    'text': text,
                    'potential_slug_fragment': os.path.basename(url).replace('.md', ''),
                    'required': '(required)' in html.lower(),
                    'recommended': '(recommended)' in html.lower()
                })
            if insight_link:
                _.append({
                    'type': 'insight',
                    'potential_name': self._extract_from_p(url_text),
                    'text': text,
                    'potential_slug_fragment': os.path.basename(url).replace('.md', ''),
                    'required': '(required)' in html.lower(),
                    'recommended': '(recommended)' in html.lower()
                })
            if workshop_link:
                _.append({
                    'type': 'workshop',
                    'potential_name': self._extract_from_p(url_text),
                    'text': text,
                    'required': '(required)' in html.lower(),
                    'recommended': '(recommended)' in html.lower()
                })
            if not install_link and not insight_link and not workshop_link:
                _.append({
                    'type': 'external_link',
                    'url_text': self._extract_from_p(url_text),
                    'text': text,
                    'url': url,
                    'required': '(required)' in html.lower(),
                    'recommended': '(recommended)' in html.lower()
                })
        fixing['prerequisites'] = _
        return fixing

    def _fix_praxis(self):
        fixing = self.sections['theory-to-practice']

        fixing['intro'] = convert_html_quotes(fixing['intro'])

        # Make lists correct
        for _list in ['discussion_questions', 'next_steps', 'tutorials', 'further_readings', 'further_projects']:
            if _list in fixing:
                fixing[_list] = [self._fix_list_element(x) for x in as_list(fixing[_list])]

        return fixing

    def _fix_image(self, dictionary):
        url = dictionary.get('url').replace('https://', '').replace('http://', '').replace(
            f'raw.githubusercontent.com/DHRI-Curriculum/{self.repository}/{self.branch}/', '')
        parents = [x for x in url.split('/') if not '.' in x]
        local_file = self.destination_dir
        for _dir in parents:
            local_file = os.path.join(local_file, _dir)
        local_file += '/' + os.path.basename(url).replace('%40', '@')
        if os.path.exists(local_file):
            return {'url': local_file, 'alt': dictionary.get('alt')}
        else:
            exit('error! fix this!') # TODO: Fix this...
            return {'url': url, 'alt': dictionary.get('alt')}

    @staticmethod
    def _check_for_lesson_sections(markdown):
        has_subheaders = len(split_into_sections(
            markdown, level_granularity=2)) > 0
        has_evaluation, has_challenge, has_solution, has_keywords = False, False, False, False

        for subheader, content in split_into_sections(markdown, level_granularity=2).items():
            if subheader.lower() == 'evaluation' or subheader.lower() == 'evaluations':
                has_evaluation = True
            if subheader.lower() == 'challenge' or subheader.lower() == 'challenges':
                has_challenge = True
            if subheader.lower() == 'solution' or subheader.lower() == 'solutions':
                has_solution = True
            if subheader.lower() == 'keyword' or subheader.lower() == 'keywords':
                has_keywords = True

        return {
            'has_subheaders': has_subheaders,
            'has_evaluation': has_evaluation,
            'has_challenge': has_challenge,
            'has_solution': has_solution,
            'has_keywords': has_keywords
        }

    def _fix_lessons(self):

        def mini_parse_eval(markdown: str):
            def reset_dict():
                return {'question': '', 'answers': {'correct': [], 'incorrect': []}}

            dict_collector = list()
            d = reset_dict()
            in_q = False

            for line in markdown.splitlines():
                is_empty = line.strip() == ''
                is_answer = line.startswith('- ')

                if not is_answer and not is_empty:
                    in_q = True
                    d['question'] += line + '\n'
                elif in_q and is_answer:
                    if line.strip().endswith('*'):
                        d['answers']['correct'].append(
                            line.strip()[2:-1].strip())
                    else:
                        d['answers']['incorrect'].append(
                            line.strip()[2:].strip())
                elif is_empty and in_q:
                    d['question'] = d['question'].strip()
                    dict_collector.append(d)
                    in_q = False
                    d = reset_dict()
                elif is_answer:
                    # stray answer belonging to the latest question so attach it...
                    try:
                        if line.strip().endswith('*'):
                            dict_collector[len(
                                dict_collector)-1]['answers']['correct'].append(convert_html_quotes(line.strip()[2:-1].strip(), strip_surrounding_body=False, strip_surrounding_p=True))
                        else:
                            dict_collector[len(
                                dict_collector)-1]['answers']['incorrect'].append(convert_html_quotes(line.strip()[2:].strip(), strip_surrounding_body=False, strip_surrounding_p=True))
                    except IndexError:
                        self.log.warning(
                            f'Found and skipping a stray answer that cannot be attached to a question: {line.strip()}')

            # add final element
            d['question'] = convert_html_quotes(d['question'].strip(), strip_surrounding_body=False, strip_surrounding_p=True)
            dict_collector.append(d)

            # clean up dict_collector
            for i, item in enumerate(dict_collector):
                if not item.get('question') and not len(item.get('answers').get('correct')) and not len(item.get('answers').get('incorrect')):
                    del dict_collector[i]
            return(dict_collector)

        _ = []
        lessons = self._get_raw()['lessons']
        lesson_sections = split_into_sections(
            lessons, level_granularity=1, clear_empty_lines=False)
        for order, lesson_data in enumerate(lesson_sections.items(), start=1):
            __ = {
                'raw_content': '',
                'order': order,
                'header': '',
                'has_lesson_sections': {},
                'content': '',
                'challenge': '',
                'solution': '',
                'keywords': '',
                'evaluation': ''
            }
            __['header'], __['raw_content'] = lesson_data
            __['has_lesson_sections'] = WorkshopCache._check_for_lesson_sections(__[
                                                                                 'raw_content'])

            if __['raw_content'].startswith('#') == False:
                __['content'] += list(split_into_sections('# '+__['header']+'\n'+__[
                                      'raw_content'], level_granularity=2).values())[0] + '\n'

            for subheader, content in split_into_sections(__['raw_content'], level_granularity=2, keep_levels=True, clear_empty_lines=False).items():
                is_evaluation = subheader.lower() == '## evaluation' or subheader.lower(
                ) == '## evaluations' or subheader.split(':')[0].lower() == '## evaluation'
                is_challenge = subheader.lower() == '## challenge' or subheader.lower(
                ) == '## challenges' or subheader.split(':')[0].lower() == '## challenge'
                is_solution = subheader.lower() == '## solution' or subheader.lower(
                ) == '## solutions' or subheader.split(':')[0].lower() == '## solution'
                is_keywords = subheader.lower() == '## keyword' or subheader.lower() == '## keywords'
                if not any([is_evaluation, is_challenge, is_solution, is_keywords]):
                    __['content'] += subheader + '\n'
                    __['content'] += self.HTML_parser(content) + '\n'
                if is_challenge:
                    __['challenge'] = {
                        'header': subheader.split('#')[-1].strip(),
                        'content': convert_html_quotes(self.HTML_parser(content))
                    }
                if is_solution:
                    __['solution'] = {
                        'header': subheader.split('#')[-1].strip(),
                        'content': convert_html_quotes(self.HTML_parser(content))
                    }
                if is_keywords:
                    __['keywords'] = {
                        'header': subheader.split('#')[-1].strip(),
                        'content': [self._fix_list_element(x) for x in as_list(content)]
                    }
                    for i, content in enumerate(__['keywords']['content']):
                        __['keywords']['content'][i]['linked_text'] = ''.join([str(x) for x in BeautifulSoup(content['linked_text'], 'lxml').p.children])
                if is_evaluation:
                    __['evaluation'] = {
                        'header': subheader.split('#')[-1].strip(),
                        'content': mini_parse_eval(content)
                    }

            # Remove raw content
            __.pop('raw_content')

            __['content'] = convert_html_quotes(self.HTML_parser(__['content']))

            _.append(__)

        return _
