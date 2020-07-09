"""
To add Zotero resources to the database:
- In [the Zotero group](https://www.zotero.org/groups/2164386/digital_humanities_research_institute/collections/AEK5CZJ6/items/ADX2JIVR/collection),
  add desired resources in whichever folder.
- Use tag "add-to-website" to indicate that the resource should be added to the website, and
- Use tag "curriculum:git" (or "curriculum:python" or "curriculum:text-analysis" etc.) to indicate which workshop to add the resource to.
- Use tag "category:project" or "category:reading" or "category:resource" to indicate which category the Zotero item belongs to

Note: this script automatically catches any URLs that are non-functional, so anything with a URL that does not generate a HTTP 200 response will mean the item will be automatically skipped.
"""

import datetime
import json
import requests
from requests.exceptions import ConnectionError
from pathlib import Path
from pyzotero import zotero
from dhri.interaction import Logger
from nameparser import HumanName
from django.utils.text import slugify
from dhri.settings import ZOTERO_API_KEY, ZOTERO_CACHE_DIR, FORCE_DOWNLOAD
from dhri.constants import TEST_AGE_ZOTERO

log = Logger(name='ZoteroCache')


def _check_age(path, age_checker=TEST_AGE_ZOTERO) -> bool:
    if isinstance(path, str): path = Path(path)

    if not path.exists() or FORCE_DOWNLOAD == True: return(False)
    file_mod_time = datetime.datetime.fromtimestamp(path.stat().st_ctime)
    now = datetime.datetime.today()

    if now - file_mod_time > age_checker:
        log.log(f'Cache has expired for {path} - older than {age_checker}...')
        return False
    else:
        # log.log(f'Cache is fine for {path} - not older than {age_checker}....')
        return True


class LocalZoteroWebpageCache():

    def __init__(self, url, force_download=FORCE_DOWNLOAD):
        self.url = url
        self.force_download = force_download

        filename = slugify(self.url[:50].replace("http://", "").replace("https://", "").replace("www.", "").replace("/", "-"))
        if filename.endswith("/"): filename = filename[:-1] # remove trailing slash
        self.path = Path(ZOTERO_CACHE_DIR) / f"{filename}.json"

        # check age of cache
        age_ok = _check_age(self.path, TEST_AGE_ZOTERO)

        if age_ok == False or self.force_download == True:
            self.url_exists = self._url_exists()
            self._write_cache()

        self.url_exists = self._read_cache()['exists']


    def _url_exists(self):
        """verifies that a URL exists"""
        try:
            r = requests.get(self.url)
        except ConnectionError:
            return False

        if r.status_code == 200:
            return True
        else:
            return False


    def _write_cache(self):
        #log.log(f'writing cache file for url {self.url}...')
        self.path.write_text(json.dumps({'exists': self.url_exists}))


    def _read_cache(self):
        #log.log(f'reading cache file for url {self.url}...')
        return(json.loads(self.path.read_text()))



class LocalZoteroCache():

    def __init__(self, api_key=ZOTERO_API_KEY, force_download=FORCE_DOWNLOAD):
        # set up basic info
        self.group_id = 2164386 # note: hard-coded for DHRI right now
        self.api = zotero.Zotero(self.group_id, 'group', api_key)
        self.data = {}
        self.api_key = api_key
        self.force_download = force_download

        # ensure we have a path
        self.path = Path(ZOTERO_CACHE_DIR) / f'{self.group_id}.json'

        # check age of cache file
        age_ok = _check_age(self.path, TEST_AGE_ZOTERO)

        if age_ok == False or self.force_download == True:
            # download data
            self._download()
            self._write_cache()

        self.data = self._read_cache()

    @property
    def collections(self):
        return(self._get_data('collections'))

    def _check_path(self):
        if not self.path.parent.exists(): self.path.parent.mkdir(parents=True)

    def _download(self):
        log.log('Downloading from Zotero library...')

        self._check_path()

        self.data = dict()

        self.data['collections'] = []
        for collection in self.api.all_collections():
            del collection['library']
            self.data['collections'].append(collection)

        log.log(f'Collections downloaded: {len(self.data["collections"])}')

        for i, collection in enumerate(self.data['collections']):
            collection_items = self.api.collection_items(self.data['collections'][i]['key'])
            self.data['collections'][i]['items'] = []
            for item in collection_items:
                del item['library']
                self.data['collections'][i]['items'].append(item)
            log.log(f'Collection items for collection {i+1} downloaded: {len(self.data["collections"][i]["items"])}')

        return(self.data)

    def _write_cache(self):
        #log.log('writing cache file...')
        self.path.write_text(json.dumps(self.data))

    def _read_cache(self):
        #log.log('reading cache file...')
        return(json.loads(self.path.read_text()))

    def _get_data(self, key):
        return(self.data.get(key, None))


class ZoteroItem():

    def __init__(self, item={},*args, **kwargs):
        self.data = item['data']
        self.key = self.data.get('key')
        self.itemType = self.data.get('itemType')
        self.abstract = self.data.get('abstractNote')
        self.title = self.data.get('title')
        self.url = self.data.get('url')
        self.url_cache = None
        if self.url: self.url_cache = LocalZoteroWebpageCache(self.url)
        self.url_exists = False
        if self.url_cache:
            self.url_exists = self.url_cache.url_exists
        self.dateAdded = self.data.get('dateAdded')
        self.blogTitle = self.data.get('blogTitle')
        self.publicationTitle = self.data.get('publicationTitle')
        self.websiteTitle = self.data.get('websiteTitle')
        self.accessDate = self.data.get('accessDate')
        self.creators = []
        if self.data.get('creators'):
            self.creators = [
                {
                    'type': x.get('creatorType'),
                    'firstName': x.get('firstName'),
                    'lastName': x.get('lastName'),
                    'name': x.get('name')
                } for x in self.data.get('creators')
            ]
            for i, _ in enumerate(self.creators):
                firstname = self.creators[i].get('firstName')
                lastname = self.creators[i].get('lastName')
                if firstname and lastname:
                    self.creators[i]['parsedName'] = HumanName(f'{firstname} {lastname}')
        self.tags = [x['tag'] for x in self.data.get('tags', [])]
        self.for_website = 'add-to-website' in self.tags

        # get curriculum and category connections
        self.curriculum, self.category = None, None
        if self.for_website:
            for tag in self.tags:
                if tag.startswith('curriculum'):
                    self.curriculum = tag[11:]
                if tag.startswith('category:'):
                    self.category = tag[9:]

    def __str__(self):
        return str(self.data)

    def get_attributes(self, attribute_list):
        _ = dict()
        for attr in attribute_list:
            _[attr] = self.data.get(attr, None)
        return _

