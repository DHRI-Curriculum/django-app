'''
This library is used for the `build` commands related to the DHRI Curriculum
'''

from git import Repo
import os
import re
from bs4 import BeautifulSoup
from nameparser import HumanName
from progressbar import UnknownLength
from shutil import copyfile
from backend.settings import CACHE_DIRS, NORMALIZING_SECTIONS, BACKEND_AUTO, STATIC_IMAGES
from backend.markdown_parser import GitHubParser, MarkdownError, PARSER, split_into_sections, as_list
from django.conf import settings


class Helper():
    IMAGE_REGEX = re.compile(r'(?:!\[(.*?)\]\((.*?)\))')

    def _extract_from_p(self, html):
        extracted = ''.join([str(x) for x in BeautifulSoup(html, 'lxml').p.children])
        return extracted

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

    def _fix_list_element(self, markdown):
        html = self.PARSER.fix_html(markdown)
        soup = BeautifulSoup(html, 'lxml')
        link = soup.find('a')
        annotation, text, url = None, None, None
        if link:
            url = link['href']
            text = link.text
        if not soup.text == text:
            annotation = html
        _ = {
            'annotation': annotation,
            'linked_text': text,
            'url': url
        }
        return _

    def _fix_image(self, dictionary, additional_parents=[]):
        if not isinstance(dictionary, dict) and not isinstance(dictionary, tuple):
            raise NotImplementedError(f'Dictionary passed in was not a dictionary but a {type(dictionary)}: {dictionary}')
        elif isinstance(dictionary, tuple):
            _ = {}
            _['url'], _['alt'] = dictionary
            dictionary = _
        url = dictionary.get('url').replace('https://', '').replace('http://', '').replace(f'raw.githubusercontent.com/DHRI-Curriculum/{self.repository}/{self.branch}/', '')
        parents = [x for x in url.split('/') if not '.' in x]
        for add_parent in additional_parents:
            if not add_parent in parents:
                parents.insert(0, add_parent)
        local_file = self.destination_dir
        for parent in parents:
            local_file = os.path.join(local_file, parent)
        local_file += '/' + os.path.basename(url).replace('%40', '@')
        if os.path.exists(local_file):
            return {'url': local_file, 'alt': dictionary.get('alt')}
        else:
            # TODO: This bug occurs when local files are not available in the parent directories
            raise NotImplementedError('This is a bug that needs to be fixed in the beta version of the website.')

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
            raise MarkdownError('Found an installation step that does not show the order clearly (see documentation). Cannot determine order: ' + str(step)) from None
        return(order, step)

    @staticmethod
    def download_image(url=None, local_file=None):
        raise DeprecationWarning('`download_image` is deprecated in this version of the website.')
        # This method should not be used since we are now implementing git cloning.

    @staticmethod
    def process_prereq_text(html, log=None):
        soup = BeautifulSoup(html, 'lxml')
        captured_link = False
        for node in soup.body.children:
            if not node.name:
                continue

            is_link = node.name.lower() == 'a'
            if is_link and not captured_link:
                captured_link = node['href']
                node.decompose()
            elif is_link and captured_link:
                log.info(f'More than one link in prerequirement. Try to keep the number of links for each prerequirement to one as it may otherwise be confusing.')
        text = ''.join([str(x) for x in soup.body.children])
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
        
        if os.path.exists(self.destination_dir) and not '.git' in os.listdir(self.destination_dir):
            self.log.info(f'Repository directory ({self.destination_dir}) exists but is not an initiated git directory, so it is removed. Contents before removal: {os.listdir(self.destination_dir)}')
            self.reset()

        if not os.path.exists(self.destination_dir):
            self.log.log(f'Repository directory does not exist so cloning: {self.destination_dir}')
            self.repo = self._clone()
        else:
            self.log.log(f'Repository directory exists so creating connection to repository: {self.destination_dir}')
            self.repo = Repo(self.destination_dir)

        self.repo.git.checkout(self.branch, force=True)

        self.log.log(f'Pulling latest repository updates from remotes origin...')
        self.repo.remotes.origin.pull()

        if self.repo.head.commit:
            latest_commit = self.repo.head.commit
            msg = f'{latest_commit}'
            if latest_commit.message:
                msg = latest_commit.message.replace('\n', ' ').strip()
            if latest_commit.author:
                msg += f' (by {latest_commit.author})'

        self.log.info(f'Checked out branch: {self.repository}/{self.branch} latest commit {msg}')

        self.parsed_data = self.parse()

    def _clone(self):
        if self.backend.lower() == 'github':
            url = f'http://www.github.com/DHRI-Curriculum/{self.repository}'
            self.log.log(f'Cloning repository from GitHub: {url}')
            self.repo = Repo.clone_from(url, self.destination_dir)
        else:
            raise NotImplementedError(f'Backend `{self.backend}` cannot be used. No implementation for it.')
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

    def read_file(self, path, skip_directories=True):
        try:
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f'Warning: File `{path}` could not be found. Run ._clone()')
        except IsADirectoryError:
            if skip_directories:
                return None
            else:
                raise IsADirectoryError()

    @classmethod
    def get_stem(self, path):
        return os.path.basename(path).split('.')[0]

    def parse(self, files=[]):
        try:
            self.log.BAR(files, max_value=len(files))
        except:
            self.log.log(f'Parsing data from repository...')

    @property
    def data(self):
        if not self.parsed_data:
            try:
                self.parsed_data = self.parse()
            except AttributeError as e:
                if 'has no attribute' in str(e) and 'parse' in str(e):
                    raise AttributeError(f'The class needs a parse method.') from None
        return self.parsed_data


class GlossaryCache(Helper, GitCache):

    def __init__(self, repository='glossary', branch='v2.0', log=None):
        self.repository = repository
        self.branch = branch
        self.cache_dir = 'GLOSSARY'
        self.log = log
        self.PARSER = GitHubParser(log=log)
        super().__init__(repository=self.repository,
                         branch=self.branch, cache_dir=self.cache_dir, log=log)

    def parse(self):
        files = self.contents_of('terms')
        super().parse(files)
        terms = []
        for i, file in enumerate(files):
            self.log.BAR.update(i)
            file_contents = self.read_file(os.path.join(self.destination_dir, 'terms', file))
            _ = {
                'term': None,
                'explication': None,
                'readings': None,
                'tutorials': None,
                'cheat_sheets': None
            }
            
            sections = split_into_sections(file_contents)
            
            for section in sections:
                if section.lower() == 'readings' or section.lower() == 'reading':
                    _['readings'] = [self._fix_list_element(x) for x in as_list(sections[section])]
                elif section.lower() == 'tutorials' or section.lower() == 'tutorial':
                    _['tutorials'] = [self._fix_list_element(x) for x in as_list(sections[section])]
                elif section.lower() == 'cheat sheets' or section.lower() == 'cheatsheets':
                    _['cheat_sheets'] = [self._fix_list_element(x) for x in as_list(sections[section])]
                else:
                    _['term'] = self.PARSER.fix_html(section)
                    _['explication'] = self.PARSER.fix_html(sections[section])
            
            terms.append(_)

        self.log.BAR.finish()
        return terms


class InstallCache(Helper, GitCache):
    cache_dir = 'INSTALL'

    def __init__(self, repository='install', branch='v2.0', log=None):
        self.repository = repository
        self.branch = branch
        self.log = log
        self.PARSER = GitHubParser(log=log)
        super().__init__(repository=self.repository,
                         branch=self.branch, cache_dir=self.cache_dir, log=log)
        self.image_baseurl = f'https://raw.githubusercontent.com/DHRI-Curriculum/{self.repository}/{self.branch}/guides/images/' # needs to end with /
        
    def parse(self):
        files = self.contents_of('guides')
        super().parse(files)
        instructions = []
        for i, file in enumerate(files):
            self.log.BAR.update(i)
            file_contents = self.read_file(os.path.join(self.destination_dir, 'guides', file))

            if not file_contents:
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
            image_data = self._get_image_from_first_line(file_contents)
            if image_data:
                image_data = self._fix_image(image_data)
                _['image_alt'] = image_data['alt']
                _['image'] = image_data['url']
                
                try:
                    file_contents = '\n'.join(file_contents.splitlines()[1:])
                except:
                    self.log.error('An error occurred when interpreting image data for installation instructions: {image_data}')

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
                    _['what'] = self.PARSER.fix_html(content.replace('---', ''))
                elif 'why we use it' in section.lower():
                    _['why'] = self.PARSER.fix_html(content.replace('---', ''))
                elif 'installation instructions' in section.lower():
                    if 'mac' in section.lower():
                        _['instructions']['macOS'] = []
                        content = split_into_sections(content)
                        for section, content in content.items():
                            __ = {}
                            __['step'], __['header'] = self._get_order(section)
                            __['html'], __['screenshots'] = self._get_screenshots_from_markdown(content, relative_dir='guides')
                            __['html'] = self.PARSER.fix_html(__['html'])
                            _['instructions']['macOS'].append(__)
                    elif 'windows' in section.lower():
                        _['instructions']['Windows'] = []
                        content = split_into_sections(content)
                        for section, content in content.items():
                            __ = {}
                            __['step'], __[
                                'header'] = self._get_order(section)
                            __['html'], __['screenshots'] = self._get_screenshots_from_markdown(content, relative_dir='guides')
                            __['html'] = self.PARSER.fix_html(__['html'])
                            _['instructions']['Windows'].append(__)
                else:
                    if not section in _['additional_sections']:
                        i += 1
                        _['additional_sections'][section] = {
                            'content': self.PARSER.fix_html(content),
                            'order': i
                        }
                    else:
                        raise MarkdownError(
                            f'Multiple sections with the same header found in the installation instructions for {_["software"]}: `{section}`. Please correct before running script again.')

            instructions.append(_)
        
        self.log.BAR.finish()
        return instructions

    def _get_screenshots_from_markdown(self, markdown='', relative_dir=None):
        screenshots = []

        html = self.PARSER.convert(markdown)
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
                self.download_image()

            if local_image:
                screenshots.append({'path': local_image, 'alt': img['alt']})
                img_data.decompose()

        for a in soup.find_all('a'):
            if a.text == '':
                a.decompose()

        html = ''.join([str(x) for x in soup.body.children])

        return html, screenshots


class InsightCache(Helper, GitCache):
    cache_dir = 'INSIGHT'

    def __init__(self, repository='insights', branch='v2.0', log=None):
        self.repository = repository
        self.branch = branch
        self.log = log
        self.PARSER = GitHubParser(log=log)
        super().__init__(repository=self.repository,
                         branch=self.branch, cache_dir=self.cache_dir, log=log)

    def parse(self):
        files = self.contents_of('pages')
        super().parse(files)
        insights = []
        for i, file in enumerate(files):
            self.log.BAR.update(i)
            file_contents = self.read_file(os.path.join(self.destination_dir, 'pages', file))
            
            if not file_contents:
                continue

            _ = {
                'image': self._get_image_from_first_line(file_contents),
                'insight': list(split_into_sections(file_contents, level_granularity=1).keys())[0],
                'introduction': '',
                'os_specific': {},
                'sections': {}
            }

            _['image'] = self._fix_image(_['image'], additional_parents=['pages'])

            sections = split_into_sections(file_contents, level_granularity=2)
            order = 0
            for section, content in sections.items():
                if section == _['insight']:
                    _['introduction'] = PARSER.fix_html(content)
                else:
                    order += 1
                    _['sections'][section] = {
                        'order': order,
                        'content': PARSER.fix_html(content)
                    }
                    has_os_specific_instruction = '### ' in content
                    if has_os_specific_instruction:
                        for operating_system, os_content in split_into_sections(content, level_granularity=3).items():
                            if operating_system == 'MacOS':
                                operating_system = 'macOS'
                            _['os_specific'][operating_system] = {
                                'content': PARSER.fix_html(os_content),
                                'related_section': section
                            }
            insights.append(_)

        self.log.BAR.finish()
        return insights


class WorkshopCache(Helper, GitCache):
    cache_dir = 'WORKSHOPS'

    def __init__(self, repository='', branch='v2.0', log=None):
        self.repository = repository
        self.branch = branch
        self.log = log
        self.PARSER = GitHubParser(log=log)
        super().__init__(repository=self.repository, branch=self.branch, cache_dir=self.cache_dir,
                         destination_dir=f'{self.CACHE_DIRS[self.cache_dir]}/{self.repository}', log=log)

        # Set up quick access
        self.name = self.data['name']
        self.frontmatter = self.sections['frontmatter']
        self.praxis = self.sections['theory-to-practice']
        self.lessons = self.sections['lessons']
        self.image = self.data['image']

    def parse(self):
        super().parse()
        data = {}
        self.raw = self._get_raw()
        data['raw'] = self.raw

        data['image'] = self._get_image_from_first_line(self.raw['image'])
        data['image'] = self._fix_image(data['image'])
        
        data['name'] = list(split_into_sections(self.raw['frontmatter'], level_granularity=1).keys())[0]
        self.sections = {key: split_into_sections(value) for key, value in self.raw.items()}
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

    def _fix_frontmatter(self):
        fixing = self.sections['frontmatter']

        # Fix estimated_time
        fixing['estimated_time'] = self._fix_estimated_time(
            fixing['estimated_time'])

        fixing['abstract'] = PARSER.fix_html(fixing['abstract'])

        # Make lists correct
        for _list in ['readings', 'projects', 'learning_objectives', 'ethical_considerations', 'cheat_sheets', 'prerequisites']:
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

            install_link = 'shortcuts/install/' in url
            insight_link = '/shortcuts/insight/' in url
            workshop_link = '/shortcuts/workshop/' in url
            
            #TODO #429: Somehow determine what is a cheatsheet and ingest that here...

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

        fixing['intro'] = PARSER.fix_html(fixing['intro'])

        # Make lists correct
        for _list in ['discussion_questions', 'next_steps', 'tutorials', 'further_readings', 'further_projects']:
            if _list in fixing:
                fixing[_list] = [self._fix_list_element(x) for x in as_list(fixing[_list])]

        return fixing

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

        def reset_eval_dict():
            return {'question': '', 'answers': {'correct': [], 'incorrect': []}}

        def mini_parse_eval(markdown: str):
            ''' Set up standards '''
            dict_collector = list()
            d = reset_eval_dict()
            in_q = False

            '''
            if '```' in markdown:
                raise NotImplementedError('Cannot parse evaluation questions with codeblocks.') from None # TODO: Build out the parser for evaluations to include code blocks. This won't do.
            '''
            
            in_code = False
            for current_line_number, line in enumerate(markdown.splitlines()):
                is_empty = line.strip() == ''
                is_answer = line.startswith('- ')

                try:
                    if markdown.splitlines()[current_line_number+1].startswith('```'):
                        print('next line contains code.. Thus this is not empty')
                        is_empty = False
                        if not in_code:
                            in_code = True
                        else:
                            in_code = False
                except IndexError:
                    pass

                if not is_answer and not is_empty:
                    in_q = True
                    d['question'] += line + '\n'
                elif in_q and is_answer:
                    if line.strip().endswith('*'):
                        answer = line.strip()[2:-1].strip()
                        answer = PARSER.fix_html(answer)
                        d['answers']['correct'].append(answer)
                    else:
                        answer = line.strip()[2:].strip()
                        answer = PARSER.fix_html(answer)
                        d['answers']['incorrect'].append(answer)
                elif is_empty and in_q and in_code == False:
                    d['question'] = d['question'].strip()
                    dict_collector.append(d)
                    in_q = False
                    d = reset_eval_dict()
                elif is_answer:
                    # stray answer belonging to the latest question so attach it...
                    try:
                        if line.strip().endswith('*'):
                            answer = line.strip()[2:-1].strip()
                            answer = PARSER.fix_html(answer)
                            dict_collector[len(dict_collector)-1]['answers']['correct'].append(answer)
                        else:
                            answer = line.strip()[2:].strip()
                            answer = PARSER.fix_html(answer)
                            dict_collector[len(dict_collector)-1]['answers']['incorrect'].append(answer)
                    except IndexError:
                        self.log.warning(
                            f'Found and skipping a stray answer that cannot be attached to a question: {line.strip()}')

            # add final element
            d['question'] = PARSER.fix_html(d['question'])
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
                'lesson_images': [],
                'challenge': {
                    'header': '',
                    'content': ''
                },
                'solution': {
                    'header': '',
                    'content': ''
                },
                'keywords': {
                    'header': '',
                    'content': []
                },
                'evaluation': {
                    'header': '',
                    'content': ''
                }
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
                    __['content'] += content + '\n'
                if is_challenge:
                    __['challenge'] = {
                        'header': subheader.split('#')[-1].strip(),
                        'content': PARSER.fix_html(content)
                    }
                if is_solution:
                    __['solution'] = {
                        'header': subheader.split('#')[-1].strip(),
                        'content': PARSER.fix_html(content)
                    }
                if is_keywords:
                    __['keywords'] = {
                        'header': subheader.split('#')[-1].strip(),
                        'content': [self._fix_list_element(x) for x in as_list(content)],
                    }
                    __['keywords']['content'] = [x.get('linked_text') for x in __['keywords']['content']]
                if is_evaluation:
                    __['evaluation'] = {
                        'header': subheader.split('#')[-1].strip(),
                        'content': mini_parse_eval(content)
                    }

            # Remove raw content
            __.pop('raw_content')

            __['header'] = PARSER.fix_html(__['header'])
            __['content'] = PARSER.fix_html(__['content'])
            __['content'], __['lesson_images'] = self._get_images_from_html(__['content'])

            # Make sure we capture images from solution as well
            add_to_lesson_images = []
            __['solution']['content'], add_to_lesson_images = self._get_images_from_html(__['solution'].get('content', ''))
            
            if add_to_lesson_images:
                before = len(__['lesson_images'])
                __['lesson_images'].extend(add_to_lesson_images)
                after = len(__['lesson_images'])
                if after - before:
                    self.log.info('Found additional images in solution, and added them to the built lesson files.')

            # Final clean-up
            for check_up in ['solution', 'challenge', 'evaluation', 'keywords']:
                if not __.get(check_up).get('content') and not __.get(check_up).get('header'):
                    __[check_up] = None
            
            _.append(__)

        return _


    def _get_images_from_html(self, html='', relative_dir=None):
        lesson_images = []

        soup = BeautifulSoup(html, 'lxml')
        
        for img_data in soup.find_all('img'):
            img = {}
            img['alt'] = img_data.get('alt')
            img['src'] = img_data.get('src')
            if not img['src']:
                self.log.warning(f"An image with no src attribute detected in installation instruction step: {img}. Skipping...")
                continue

            if img['src'].startswith('/'):
                # we have an absolute image, so we should be able to get local_image from this path
                local_image = (str(self.destination_dir) + '/' + img['src']).replace('//', '/')
            else:
                # we have a relative image, so construct its entire path in the repo
                local_image = self.destination_dir
                if relative_dir:
                    local_image = os.path.join(local_image, relative_dir)
                for _dir in [x for x in img['src'].split('/') if not '.' in x]:
                    local_image = os.path.join(local_image, _dir)
                local_image += '/' + os.path.basename(img['src'])

            if os.path.exists(local_image):
                pathdir = os.path.join(STATIC_IMAGES['LESSONS'], self.repository)
                if not os.path.exists(pathdir):
                    os.mkdir(pathdir)
                new_path = os.path.join(STATIC_IMAGES['LESSONS'], self.repository, os.path.basename(local_image))
                if not os.path.exists(new_path):
                    copyfile(local_image, new_path)
            else:
                raise NotImplementedError('This script does not yet download images as it should be synced in the repository.')

            path = settings.STATIC_URL + f'website/images/lessons/{self.repository}/' + os.path.basename(local_image)
            img_data['src'] = path
            if img_data.parent.name == 'a':
                img_data.parent['href'] = None
                img_data.parent['target'] = None

            lesson_images.append({'path': path, 'alt': img['alt']})

        if not soup.body:
            html = ''
        else:
            html = ''.join([str(x) for x in soup.body.children])

        return html, lesson_images

        

