import json
import re
import requests

from pathlib import Path
from collections import OrderedDict
from bs4 import BeautifulSoup

from .log import Logger, log_created
from .loader import _is_expired, download_image
from .markdown import split_into_sections
from .markdown_parser import PARSER

from backend.dhri_settings import FORCE_DOWNLOAD, TEST_AGES, CACHE_DIRS, STATIC_IMAGES, INSTALL_REPO

# TODO: Move to backend.dhri_settings
IMAGE_CACHE = {
    'INSTALL': '.loader-cache/images/install'
}
for _, dir in IMAGE_CACHE.items():
    IMAGE_CACHE[_] = Path(dir)
    if not IMAGE_CACHE[_].exists(): IMAGE_CACHE[_].mkdir(parents=True)


class InstallCache():

    log = Logger(name='install-loader-cache')

    def __init__(self, loader, force_download=FORCE_DOWNLOAD):
        self.loader = loader

        self.path = CACHE_DIRS['ROOT'] / (self.loader.repo_name + ".json")
        self.expired = _is_expired(self.path, age_checker=TEST_AGES["INSTALL"], force_download=force_download) == True

        if not self.path.exists():
            self.log.warning(f'{self.path} does not exist so downloading install cache...')
            self._setup_raw_content()

        if force_download == True:
            self.log.warning(f'Force download is set to True so downloading install cache...')
            self._setup_raw_content()

        if self.expired == True:
            self.log.warning(f'File is expired (set to {self.expired}) so downloading install cache...')
            self._setup_raw_content()

        self.data = self.load()


    def _setup_raw_content(self):
        self.data = {
            'raw': self._load_raw_text()
        }

        self.save()


    def _load_raw_text(self):
        self.log.log(f'Loading raw text from {self.loader.repo_name}...')

        r = requests.get(f'https://github.com/DHRI-Curriculum/{self.loader.repo_name}/tree/{self.loader.branch}/guides')

        soup = BeautifulSoup(r.text, 'lxml')

        results = dict()

        for _ in soup.find_all("div", {"class": "js-navigation-item"})[1:]:
            link = _.find('a')['href']
            filename = link.split('/')[-1]
            name = ".".join(filename.split('.')[:-1])

            if name != 'images' and name != '':
                self.log.log(f'Loading raw text from `{name}`...')
                raw_url = f'https://raw.githubusercontent.com/DHRI-Curriculum/{self.loader.repo_name}/{self.loader.branch}/guides/{filename}'
                r = requests.get(raw_url)
                results[name] = r.text

        return(results)


    def save(self):
        """Saves <self.data> into <self.path>"""
        if not self.path.parent.exists(): self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps(self.data))


    def load(self):
        """Loads <self.data> from <self.path>"""
        return json.loads(self.path.read_text())


class InstallParser():

    log = Logger(name='install-parser')

    def _get_order(self, step):
        g = re.search(r"Step ([0-9]+): ", step)
        if g:
            order = g.groups()[0]
            step = re.sub(r'Step ([0-9]+): ', '', step)
        else:
            order = 0
            self.log.warning('Found an installation step that does not show the order clearly (see documentation). Cannot determine order: ' + str(step))
        return(order, step)

    software, what, why, windows, mac_os = None, None, None, None, None
    _instructions, instructions, additional_sections = dict(), {'mac os': '', 'windows': ''}, OrderedDict()

    def __init__(self, data:str):
        self.software = list(split_into_sections(data, level_granularity=1).keys())[0]

        for section, text in split_into_sections(data, level_granularity=2).items():
            if text == '': continue
            if 'remove this section' in section.lower(): continue # automatically remove sections that contain this text

            if 'what it is' in section.lower():
                text = text.replace('---', '') # manually removing this because it causes issues with paragraphs being converted to h2
                self.what = PARSER.convert(text) # make it into HTML
                continue
            if 'why we use it' in section.lower():
                text = text.replace('---', '') # manually removing this because it causes issues with paragraphs being converted to h2
                self.why = PARSER.convert(text) # make it into HTML
                continue
            if 'installation instructions' in section.lower() and 'macos' in section.lower():
                self.instructions['mac os'] = text
                continue
            if 'installation instructions' in section.lower() and 'windows' in section.lower():
                self.instructions['windows'] = text
                continue
            self.additional_sections[section] = text

        # Correct the instruction lists into sections
        operating_systems = ['mac os', 'windows']
        for os in operating_systems:
            if self.instructions[os] and isinstance(self.instructions[os], str):
                self._instructions[os] = dict()
                self.instructions[os] = split_into_sections(self.instructions[os], level_granularity=3)

                for section, text in self.instructions[os].items():
                    order, header = self._get_order(section)
                    self._instructions[os][section] = {
                        'header': header,
                        'text': text,
                        'html': PARSER.convert(text), # make it into HTML
                        'screenshots': list(),
                        'order': order
                    }

                    # find images
                    soup = BeautifulSoup(self._instructions[os][section]['html'], 'lxml')
                    for img in soup.find_all("img"):
                        src = img.get('src')
                        if not src:
                            self.log.warning(f"An image with no src attribute detected in installation instruction step: {img}. Skipping...")
                            continue

                        filename = src.split('/')[-1]

                        if filename == '%3Cfilename.png%3E':
                            print('skipping...')
                            continue

                        local_file = IMAGE_CACHE['INSTALL'] / filename

                        url = f'https://raw.githubusercontent.com/DHRI-Curriculum/{INSTALL_REPO[0]}/{INSTALL_REPO[1]}/guides/images/{filename}'
                        if '//' in url:
                            url = url.replace('//', '/').replace('https:/', 'https://').replace('http:/', 'http://')

                        _ = download_image(url, local_file)

                        local_url = f'/media/installation_screenshots/{INSTALL_REPO[0]}/{filename}'

                        self._instructions[os][section]['screenshots'].append((filename, str(_), local_url))

                        img.decompose()

                    # remove all empty a hrefs
                    for a in soup.find_all('a'):
                        if a.text == '': a.decompose()

                    # manual fixes
                    soup = str(soup).replace('\n</', '</').replace('---', '<hr />')
                    self._instructions[os][section]['html'] = str(soup).replace('<html><body>', '').replace('</body></html>', '')
                else:
                    self.log.warning('Expected instructions to be a markdown string but received an object of type `dict`. Continuing assuming that `dict` object contains valid instructions.')
        self.instructions['windows'] = self._instructions['windows']
        self.windows = self.instructions['windows']

        self.instructions['mac os'] = self._instructions['mac os']
        self.mac_os = self.instructions['mac os']

        '''
        if self.instructions['mac os']:
            self.instructions['mac os'] = split_into_sections(self.instructions['mac os'], level_granularity=3)

            for section, text in self.instructions['mac os'].items():
                self.instructions['mac os'][section] = PARSER.convert(text) # make it into HTML

        self.mac_os = self.instructions['mac os']
        '''


class InstallLoader():

    log = Logger(name='install-loader')

    instructions = dict()
    all_software = list()

    def __init__(self, install_repo=INSTALL_REPO, force_download=FORCE_DOWNLOAD):
        self.repo_name = install_repo[0]
        self.branch = install_repo[1]

        self.data = InstallCache(self, force_download=force_download).data

        # Map properties
        self.raw = self.data.get('raw')

        for _, content in self.data.get('raw').items():
            software = list(split_into_sections(content, level_granularity=1).keys())[0]
            self.all_software.append(software)
            p = InstallParser(content)
            self.instructions[software] = p