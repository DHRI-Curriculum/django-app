import datetime
import json
from pathlib import Path
from pyzotero import zotero



API_KEY = Path('./zotero-api-key.txt').read_text()
CACHE_DIR = './__zotero-cache__/'
TEST_AGE = datetime.timedelta(days=2) # every two days
FORCE_DOWNLOAD = False



def _check_age(path, age_checker=TEST_AGE) -> bool:
    if isinstance(path, str): path = Path(path)

    if not path.exists() or FORCE_DOWNLOAD == True: return(False)
    file_mod_time = datetime.datetime.fromtimestamp(path.stat().st_ctime)
    now = datetime.datetime.today()

    if now - file_mod_time > age_checker:
        print(f'Cache has expired for {path} - older than {age_checker}...')
        return False
    else:
        # print(f'Cache is fine for {path} - not older than {age_checker}....')
        return True


class LocalZoteroCache():

    def __init__(self, api_key=API_KEY, force_download=FORCE_DOWNLOAD):
        # set up basic info
        self.group_id = 2164386
        self.api = zotero.Zotero(self.group_id, 'group', api_key)
        self.data = {}
        self.api_key = api_key
        self.force_download = force_download

        # ensure we have a path
        self.path = Path(CACHE_DIR) / f'{self.group_id}.json'

        # check age of cache file
        age_ok = _check_age(self.path, TEST_AGE)

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
        print('Downloading...')
        self.data = dict()

        self.data['collections'] = []
        for collection in self.api.all_collections():
            del collection['library']
            self.data['collections'].append(collection)

        for i, collection in enumerate(self.data['collections']):
            collection_items = self.api.collection_items(self.data['collections'][i]['key'])
            self.data['collections'][i]['items'] = []
            for item in collection_items:
                del item['library']
                self.data['collections'][i]['items'].append(item)

        return(self.data)

    def _write_cache(self):
        print('writing cache file...')
        self.path.write_text(json.dumps(self.data))

    def _read_cache(self):
        print('reading cache file...')
        return(json.loads(self.path.read_text()))

    def _get_data(self, key):
        return(self.data.get(key, None))


zotero = LocalZoteroCache(force_download=True)