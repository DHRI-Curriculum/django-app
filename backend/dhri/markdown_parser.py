import markdown
import time
import json

from github import Github

from backend.dhri.log import Logger
from backend.dhri_settings import CACHE_DIRS, FORCE_DOWNLOAD
from django.utils.text import slugify
from django.conf import settings

log = Logger(name='github-parser')


class GitHubParserCache():

    def __init__(self, string:str=None, force_download=FORCE_DOWNLOAD):
        from backend.dhri.loader import _is_expired
        self.string = string
        self.path = CACHE_DIRS['PARSER'] / (f'{slugify(string[:100])}.json')

        if not self.path.exists() or force_download == True or _is_expired(self.path, force_download=force_download) == True:
            self.data = self._setup_raw_content()
            self.save()
        elif self.path.exists():
            self.data = self.load()
            if self._check_length() == False or self._gh_processed() == False: # Checking whether the length of the string cached has changed (``_check_length``) or whether GitHub processed the string in the first place (``_gh_processed``) — if not, run processor again
                self.data = self._setup_raw_content()
                self.save()

        self.data = self.load()

        self.data = self.process(self.data)


    def process(self, data:dict):
        markdown = data.get('markdown')
        if markdown:
            markdown = markdown.replace('  ', '&nbsp;&nbsp;').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
            data['markdown'] = markdown
        return data

    def load(self):
        """Loads <self.data> from <self.path>"""
        return json.loads(self.path.read_text())


    def save(self):
        """Save <self.data> to <self.path>"""
        self.path.write_text(json.dumps(self.data))
        return True


    def _gh_processed(self):
        return self.data.get('processor', '').lower() == 'github'


    def _check_length(self):
        return len(self.data.get('original_string', '')) == len(self.string)


    def _setup_raw_content(self):
        """Queries GitHub for the html text for a given string"""
        if not settings.GITHUB_TOKEN:
            log.error('GitHub API token is not correctly set up in backend.dhri_settings — correct the error and try again')

        string = str(self.string)
        g = Github(settings.GITHUB_TOKEN)

        exceptions = list()
        fatal = False

        try:
            rendered_str = g.render_markdown(string)
            processor = 'GitHub'
        except Exception as e:
            exceptions.append(str(e))
            time.sleep(3)
            try:
                rendered_str = g.render_markdown(string)
                processor = 'GitHub'
            except:
                exceptions.append(str(e))

                log.error(f'GitHub API interpretation of markdown failed: Trying to interpret data using internal markdown instead.', kill=False)
                log.error(f'FYI, these were the exceptions:', kill=False)
                log.error("\n- ".join(exceptions), kill=False)

                fatal = True

        if 'triggered an abuse detection mechanism' in rendered_str.lower():
            fatal = True

        if 'bad credentials' in rendered_str.lower():
            fatal = True

        if fatal:
            # backup solution
            p = markdown.Markdown(extensions=['extra', 'codehilite', 'sane_lists'])
            rendered_str = p.convert(string)
            processor = 'Markdown'

        return({
            'original_string': self.string,
            'markdown': rendered_str,
            'processor': processor
        })


class GitHubParser():

    def __init__(self, string:str=None):
        pass


    def convert(self, string):
        c = GitHubParserCache(string=string)
        return(c.data.get('markdown', ''))


PARSER = GitHubParser()