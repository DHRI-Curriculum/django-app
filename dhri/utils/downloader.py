import requests

from .markdown import split_into_sections

BRANCH_AUTO = 'v2.0'

class Error():
    # TODO: Should be a dhri_error but gotta fix that later
    def __init__(self, message, kill=True):
        print(message)
        if kill: exit()


class DownloaderCache():

    def __init__(self, repo):
        print(repo)


class Downloader():
    """
    Downloads all the raw content from a provided repository on GitHub, and from a particular master.

    The repository must be *public* and must contain the following three files:
    - frontmatter.md
    - theory-to-practice.md
    - assessment.md
    """
    meta = {}
    content = {}
    
    def __init__(self, repo='https://www.github.com/kallewesterling/dhri-test-repo', branch=BRANCH_AUTO):
        self.repo = repo
        self.branch = branch

        self._verify_repo()
        
        self.user = self.repo.split('/')[3]
        self.repo_name = self.repo.split('/')[4]
        
        # Set up raw urls
        self._raw_url = f'https://raw.githubusercontent.com/{self.user}/{self.repo_name}/{self.branch}'
        
        self.frontmatter_path = f'{self._raw_url}/frontmatter.md'
        self.praxis_path = f'{self._raw_url}/theory-to-practice.md'
        self.assessment_path = f'{self._raw_url}/assessment.md'

        self._get_raw_content()

        self._frontmatter_raw = self.content.get('frontmatter')
        self._praxis_raw = self.content.get('theory-to-practice')
        self._assessment_raw = self.content.get('assessment')

        self._frontmatter = split_into_sections(self._frontmatter_raw)
        self._praxis = split_into_sections(self._praxis_raw)
        self._assessment = split_into_sections(self._assessment_raw)

    
    @property
    def frontmatter(self):
        return self._frontmatter
        
    @property
    def praxis(self):
        return self._praxis
        
    @property
    def assessment(self):
        return self._assessment
        
        
    def _get_raw_content(self):
        self.meta = {
                'raw_urls': {
                    'frontmatter': self.frontmatter_path,
                    'praxis': self.praxis_path,
                    'assessment': self.assessment_path
                },
                'repo_url': self.repo,
                'user': self.user,
                'repo_name': self.repo_name,
                'branch': self.branch,
            }
        self.content = {
                'frontmatter': self._get_live_text_from_url(self.frontmatter_path),
                'theory-to-practice': self._get_live_text_from_url(self.praxis_path),
                'assessment': self._get_live_text_from_url(self.assessment_path),
            }

    def _get_live_text_from_url(self, url):
        """ # TODO: insert docstring here """
        from requests.exceptions import HTTPError

        r = requests.get(url)
        print(r.status_code)

        try:
            r.raise_for_status()
        except HTTPError as e:
            Error(f'The URL ({url}) could not be used. Verify that you are using the correct repository, and that the branch that you provide is correct.')
        return(r.text)

    def _verify_repo(self):
        """ Verifies that a provided repository string is correct. Returns a string with corrected information """

        # TODO: This function doubles up with verify_url() from .meta

        if self.repo == None:
            Error('No repository URL provided.', raise_error=RuntimeError)

        if self.repo.endswith('/'):
            self.repo = self.repo[:-1]

        if len(self.repo.split('/')) != 5:
            Error()(f'Cannot interpret repository URL {self.repo}. Are you sure it is a simple https://github.com/user-name/repo link?', raise_error=RuntimeError)
