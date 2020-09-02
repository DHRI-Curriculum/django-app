import json
import requests

from bs4 import BeautifulSoup
from collections import OrderedDict

from backend.dhri.log import Logger, log_created
from backend.dhri_settings import FORCE_DOWNLOAD, TEST_AGES, CACHE_DIRS, INSIGHT_REPO, STATIC_IMAGES
from backend.dhri.loader import _is_expired
from backend.dhri.markdown import split_into_sections
from backend.dhri.markdown_parser import PARSER
from backend.dhri.loader import download_image

class InsightCache():

    log = Logger(name='insight-loader-cache')

    def __init__(self, loader, force_download=FORCE_DOWNLOAD):
        self.loader = loader

        self.path = CACHE_DIRS['ROOT'] / (self.loader.repo_name + ".json")
        self.expired = _is_expired(self.path, age_checker=TEST_AGES["INSIGHT"], force_download=force_download) == True
        if self.expired and force_download: self.expired = False

        if not self.path.exists() or force_download == True or self.expired == True:
            if not self.path.exists(): self.log.warning(f'{self.path} does not exist so downloading install cache...')
            if force_download == True: self.log.warning(f'Force download is set to True so downloading install cache...')
            if self.expired == True: self.log.warning(f'File is expired (set to {self.expired}) so downloading install cache...')
            self._setup_raw_content()

        self.data = self.load()


    def _setup_raw_content(self):
        self.data = {'raw': self._load_raw_text()}
        self.save()


    def _load_raw_text(self):
        self.log.log(f'Loading raw text from {self.loader.repo_name}...')

        r = requests.get(f'https://github.com/DHRI-Curriculum/{self.loader.repo_name}/tree/{self.loader.branch}/pages')
        soup = BeautifulSoup(r.text, 'lxml')

        results = dict()

        for link in soup.find_all('a', {'class': 'js-navigation-open'}):
            if 'pages' in link.get('href') and not link.text == 'images':
                link = link.get('href')
                filename = link.split('/')[-1]
                name = ".".join(filename.split('.')[:-1])

                if name != '':
                    self.log.log(f'Loading raw text from `{name}`...')
                    raw_url = f'https://raw.githubusercontent.com/DHRI-Curriculum/{self.loader.repo_name}/{self.loader.branch}/pages/{filename}'
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




class InsightLoader():

    log = Logger(name='insight-loader')

    def __init__(self, insight_repo=INSIGHT_REPO, force_download=FORCE_DOWNLOAD):
        self.repo_name = insight_repo[0]
        self.branch = insight_repo[1]

        self.insights = dict()
        self.all_insights = list()

        self.data = InsightCache(self, force_download=force_download).data

        # Map properties
        self.raw = self.data.get('raw')

        for _, content in self.data.get('raw').items():
            insight = list(split_into_sections(content, level_granularity=1).keys())[0]
            self.all_insights.append(_)
            p = InsightParser(content, loader=self)
            self.insights[_] = p
            self.insights[_].header = insight.strip()


class InsightParser():

    log = Logger(name='insight-parser')

    def __init__(self, data:str, loader=None):
        self.loader = loader
        self.insight = list(split_into_sections(data, level_granularity=1).keys())[0]
        self._sections = split_into_sections(data, level_granularity=2)
        self.sections = OrderedDict()
        self.os_specific = OrderedDict()
        self.introduction = None
        self.has_os_specific_instructions = False

        if '### ' in data:
            self.has_os_specific_instructions = True

        for section, text in self._sections.items():
            if section == self.insight:
                if text:
                    self.introduction = PARSER.convert(text) # make it into HTML
            else:
                if self.has_os_specific_instructions == True:
                    for os, text2 in split_into_sections(text, level_granularity=3).items():
                        self.os_specific[os] = {
                            'section': section
                        }
                        if text2:
                            self.os_specific[os]['text'] = PARSER.convert(text2) # make it into HTML
                        if section not in self.sections:
                            self.sections[section] = ''
                else:
                    if text:
                        self.sections[section] = PARSER.convert(text) # make it into HTML
                    else:
                        self.sections[section] = ''

        def replace_images(soup):
            imgs = soup.find_all('img')
            if imgs:
                for img in imgs:
                    src = img.get('src')
                    if not src:
                        self.log.warning(f"An image with no src attribute detected in lesson: {image}")
                        continue
                    filename = img['src'].split('/')[-1]
                    url = f'https://raw.githubusercontent.com/DHRI-Curriculum/{self.loader.repo_name}/{self.loader.branch}/pages/images/{filename}'
                    local_file = STATIC_IMAGES['INSIGHT'] / filename

                    if '//' in url:
                        url = url.replace('//', '/').replace('https:/', 'https://').replace('http:/', 'http://')

                    download_image(url, local_file)
                    local_url = f'/static/insight/images/{filename}'
                    img['src'] = local_url
                    img['class'] = img.get('class', []) + ['img-fluid', 'd-block', 'my-4']
            links = soup.find_all('a')
            if links:
                for img_link in [x for x in links if '.jpg' in x.get('href', '') or '.png' in x.get('href', '') or '.gif' in x.get('href', '')]:
                    img_link.replaceWithChildren()
            return soup

        def get_soup_str(soup):
            return str(soup).replace('<html><body>', '').replace('</body></html>', '').strip()

        # Check for images
        for section, html in self.sections.items():
            soup = BeautifulSoup(str(html), 'lxml')
            soup = replace_images(soup)
            self.sections[section] = get_soup_str(soup)

        for section, d in self.os_specific.items():
            soup = BeautifulSoup(str(d['text']), 'lxml')
            soup = replace_images(soup)
            self.os_specific[section]['text'] = get_soup_str(soup)
