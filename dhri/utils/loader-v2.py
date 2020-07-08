# An upgraded and better (faster) loader


class LoaderCache(Loader):
    from pathlib import Path
    import json


    def __init__(self, loader, force_download=FORCE_DOWNLOAD):
        self.loader = loader
        self.force_download = force_download

        self.path = Path(DOWNLOAD_CACHE_DIR) / (self.loader.repo_name + ".json")
        if not self.path.exists() or force_download: self._setup_raw_content()

        self.data = self.load()


    def _setup_raw_content(self):
        self.data = {
            'frontmatter': self._load_raw_text(f'{self.loader.base_url}/frontmatter.md'),
            'praxis': self._load_raw_text(f'{self.loader.base_url}/theory-to-practice.md'),
            'assessment': self._load_raw_text(f'{self.loader.base_url}/assessment.md'),
            'lessons': self._load_raw_text(f'{self.loader.base_url}/lessons.md')
        }
        self.save()


    def save(self):
        if not self.path.parent.exists(): self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps(self.data))


    def load(self):
        return json.loads(self.path.read_text())


    def _load_raw_text(self, url=""):
        from requests.exceptions import HTTPError, MissingSchema

        try:
            r = requests.get(url)
        except MissingSchema:
            print("Error: Incorrect URL")
            return("")

        try:
            r.raise_for_status()
        except HTTPError:
            self.log.error(f'The URL ({url}) could not be used. Verify that you are using the correct repository, and that the branch that you provide is correct.', raise_error=HTTPError)

        return(r.text)


    @property
    def frontmatter(self):
        return self.data.get('frontmatter')


    @property
    def praxis(self):
        return self.data.get('praxis')


    @property
    def assessment(self):
        return self.data.get('assessment')


    @property
    def lessons(self):
        return self.data.get('lessons')


class Loader():

    def __init__(self, repo=REPO_AUTO, branch=BRANCH_AUTO, download=True, force_download=FORCE_DOWNLOAD):
        self.repo = repo
        self.branch = branch
        self.download = download
        self.force_download = force_download

        self.user = self.repo.split('/')[3]
        self.repo_name = self.repo.split('/')[4]

        self.base_url = f'https://raw.githubusercontent.com/{self.user}/{self.repo_name}/{self.branch}'

        self.cache = LoaderCache(self)

        self.data = self.cache.data
        self.html_data = {k: markdown.markdown(v) for k, v in self.data.items()}
