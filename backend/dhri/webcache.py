from django.utils.text import slugify
from urllib import parse as urlparser
from backend.dhri.log import Logger

from backend.dhri_settings import FORCE_DOWNLOAD
from backend.dhri_settings import CACHE_DIRS, TEST_AGES, DO_NOT_DOWNLOAD

import requests
import json
import datetime
from requests.exceptions import ProxyError
from pathlib import Path
from bs4 import BeautifulSoup


log = Logger(name='webcache')

class WebCache():

    def _get_path_from_url(self, url):
        parsed = urlparser.urlparse(url)
        elem = parsed.netloc.split('.')
        elem.reverse()
        json_path = parsed.path
        if json_path.endswith('/'): json_path = json_path[:-1]
        if json_path.startswith('/'): json_path = json_path[1:]
        json_path = json_path.replace('/', '-')
        slugified = slugify(json_path) or 'none'
        return CACHE_DIRS['WEB'] / ('/'.join([x for x in elem if not x == 'www']) + '/' + slugified + '.json')

    def _valid_url(self):
        from django.core.validators import URLValidator
        validate = URLValidator()
        try:
            validate(self.url)
            return True
        except:
            return False

    def _ensure_parents(self, path):
        if not path.parent.exists(): path.parent.mkdir(parents=True)

    def __init__(self, url:str, force_download=FORCE_DOWNLOAD):
        self.url = url
        self.valid_url = self._valid_url()
        self.data = dict()
        self.title = None
        self.status_code = None
        self.force_download = FORCE_DOWNLOAD

        if not self.valid_url:
            log.error(f'Not a valid URL: {self.url}', kill=None)
            self.data = {
                'title': '',
                'status_code': None,
            }

        if self.valid_url:
            #slug_url = self.replace_trailing_slash(url)
            #slug_url = self.pre_clean_url(url)
            # self.path = CACHE_DIRS['WEB'] / (slugify(slug_url)+'.json')
            self.path = self._get_path_from_url(url)
            self.path = Path(self.path)
            self._ensure_parents(self.path)

            self._check_age()

            if not self.path.exists():
                self.data = self.download()
                self.save()

            if self.path.exists():
                self.data = self.load()
                if isinstance(self.data, dict):
                    self.title = self.data.get('title')
                    self.status_code = self.data.get('status_code')
        else:
            self.title = ''
            self.status_code = None

    def save(self):
        self.path.write_text(json.dumps(self.data))

    def replace_trailing_slash(self, url:str):
        if url.endswith('/'): url = url[:-1]
        return url

    def download(self):
        if self.url != None and str(self.url).lower().strip() == 'none' and str(self.url).lower().strip() == '':
            return('')
        else:
            log.log(f'Trying to download cache for URL: {self.url}')
            if not self.url.startswith('http'):
                if not self.url.startswith('#'):
                    self.url = f'http://{self.url}'
                else:
                    return ''
            if self.url in DO_NOT_DOWNLOAD:
                log.warning(f'{self.url} was detected, a file listed not for download.')
                return ''
            
            try:
                r = requests.get(self.url, timeout=10)
                soup = BeautifulSoup(r.text, 'lxml')
                try:
                    return {
                        'title': soup.find('title').text,
                        'status_code': r.status_code,
                    }
                except:
                    return ''
            except ProxyError as e:
                log.warning(f'Could not access {self.url} because of a proxy error: {e}')
                return('')
            except Exception as e:
                log.warning(f'Could not access {self.url} because of a fatal error: {e}')
                return('')

    def load(self):
        return json.loads(self.path.read_text())

    def _check_age(self) -> bool:
        if not self.path.exists() or self.force_download == True: return(False)
        file_mod_time = datetime.datetime.fromtimestamp(self.path.stat().st_ctime)
        now = datetime.datetime.today()

        if now - file_mod_time > TEST_AGES['WEB']:
            try:
                self.parent.log.log(f'Cache has expired - older than {TEST_AGES["WEB"]} minutes... Removing.')
            except:
                log.log(f'Cache has expired - older than {TEST_AGES["WEB"]} minutes... Removing.')
            self.path.unlink()
            return False
        else:
            return True