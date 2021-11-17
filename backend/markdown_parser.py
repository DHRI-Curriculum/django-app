import markdown
import time
import re
import datetime
import json
import pathlib
import os
import smartypants

from backend.logger import Logger
from backend.settings import AUTO_REPOS, CACHE_DIRS, FORCE_DOWNLOAD, TEST_AGES, CACHE_VERBOSE, GITHUB_TOKEN
from django.utils.text import slugify
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from collections import OrderedDict

from github import Github
from bs4 import BeautifulSoup

log = Logger(name='github-parser')


def _is_expired(path, age_checker=TEST_AGES['ROOT'], force_download=FORCE_DOWNLOAD) -> bool:
    """Checks the age for any path against a set expiration date (a timedelta)"""

    if isinstance(path, str):
        path = pathlib.Path(path)
    log = Logger(name='cache-age-check')
    if not path.exists() or force_download == True:
        return(True)
    file_mod_time = datetime.datetime.fromtimestamp(path.stat().st_ctime)
    now = datetime.datetime.today()

    if now - file_mod_time > age_checker:
        log.warning(
            f'Cache has expired for {path} - older than {age_checker}...')
        return True

    if CACHE_VERBOSE == True:
        log.log(
            f'Cache is OK for {path} - not older than {age_checker}....', force=True)
    return False


class GitHubParserCache():

    def __init__(self, string: str = None, force_download=FORCE_DOWNLOAD):
        self.string = string
        self.path = CACHE_DIRS['PARSER'] / f'{len(self.string)}{slugify(string[:100])}.json'

        if not self.path.exists() or force_download == True or _is_expired(self.path, force_download=force_download) == True:
            # print('loading github parser...')
            self.data = self._setup_raw_content()
            self.save()
        elif self.path.exists():
            self.data = self.load()
            # Checking whether the length of the string cached has changed (``_check_length``) or whether GitHub processed the string in the first place (``_gh_processed``) — if not, run processor again
            if self._gh_processed() == False:  # self._check_length() == False or  (this should be part of the filename now)
                # print('reloading github parser...')
                self.data = self._setup_raw_content()
                self.save()

        self.data = self.load()
        self.data = self.process(self.data)

    def process(self, data: dict):
        markdown = data.get('markdown')
        if markdown:
            markdown = markdown.replace('  ', '&nbsp;&nbsp;').replace(
                '\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
            data['markdown'] = markdown.strip()
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
        if not GITHUB_TOKEN:
            log.error('GitHub API token is not correctly set up in backend.settings — correct the error and try again')

        string = str(self.string)
        g = Github(GITHUB_TOKEN)

        exceptions = list()
        fatal = False
        rendered_str = ''

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

                log.error(
                    f'GitHub API interpretation of markdown failed: Trying to interpret data using internal markdown instead.', kill=False)
                log.error(f'FYI, these were the exceptions:', kill=False)
                log.error("\n- ".join(exceptions), kill=False)

                fatal = True
        print(f'{processor} rendered markdown: {rendered_str}')
        if 'triggered an abuse detection mechanism' in rendered_str.lower() or 'you have exceeded a secondary rate limit' in rendered_str.lower():
            fatal = True

        if 'bad credentials' in rendered_str.lower():
            fatal = True

        if fatal:
            # backup solution
            p = markdown.Markdown(
                extensions=['extra', 'codehilite', 'sane_lists'])
            rendered_str = p.convert(string)
            processor = 'Markdown'

        return {
            'original_string': self.string,
            'markdown': rendered_str,
            'processor': processor
        }


class GitHubParser():

    def __init__(self, string: str = None, log=None):
        if log == None:
            self.log = Logger(name='github-parser')
        else:
            self.log = log

    def convert(self, string):
        c = GitHubParserCache(string=string)
        return(c.data.get('markdown', '').strip())

    def strip_from_p(self, html):
        soup = BeautifulSoup(html, 'lxml')
        if soup.p:
            return ''.join([str(x) for x in soup.p.children])
        else:
            return html

    def _fix_link(self, tag):
        def find_workshop(elements):
            if elements[-1] == 'DHRI-Curriculum':
                return '{GH_CURRICULUM}'
            for element in elements:
                for workshop in [x[0] for x in AUTO_REPOS]:
                    if workshop == element: return workshop
            return ''

        elements = tag['href'].split('/')

        if 'http:' in elements or 'https:' in elements:
            link_type = 'absolute'
        elif elements[0].startswith('#'):
            link_type = 'local'
        else:
            link_type = 'relative'
        
        raw_file = False
        if link_type == 'absolute':
            if 'DHRI-Curriculum' in elements:
                if 'glossary' in elements and 'terms' in elements:
                    term = elements[-1].replace('.md', '')
                    self.log.info(f'Found link to an **glossary term** and adding shortcut link to: curriculum.dhinstitutes.org/shortcuts/term/{term}')
                    tag['href'] = f'https://curriculum.dhinstitutes.org/shortcuts/term/{term}'
                elif 'insights' in elements and 'pages' in elements:
                    insight = elements[-1].replace(".md", "")
                    self.log.info(f'Found link to an **insight** and adding shortcut link to: curriculum.dhinstitutes.org/shortcuts/insight/{insight}')
                    tag['href'] = f'https://curriculum.dhinstitutes.org/shortcuts/insight/{insight}'
                elif 'install' in elements and 'guides' in elements:
                    install = elements[-1].replace(".md", "")
                    self.log.info(f'Found link to an **installation** and adding shortcut link to: curriculum.dhinstitutes.org/shortcuts/install/{install}')
                    tag['href'] = f'https://curriculum.dhinstitutes.org/shortcuts/install/{install}'
                elif 'raw.githubusercontent.com' in elements:
                    raw_link = '/'.join(elements)
                    self.log.info(f'Found link to **raw file** and will not change link: {raw_link}')
                else:
                    workshop = find_workshop(elements)
                    if workshop == '{GH_CURRICULUM}':
                        gh_link = '/'.join(elements)
                        self.log.info(f'Link found to **the DHRI Curriculum on GitHub**, linking to it: {gh_link}')
                    elif workshop == '':
                        gh_link = '/'.join(elements)
                        self.log.warning(f'Found link to workshop, which is not currently being loaded into the website, will therefore redirect to **workshop on GitHub**: {gh_link}')
                    else:
                        self.log.info(f'Found link to **workshop** which (will) exist(s) on website, so changing to that: curriculum.dhinstitutes.org/workshops/{workshop}')
                        tag['href'] = f'https://curriculum.dhinstitutes.org/shortcuts/workshop/{workshop}'
            else:
                pass # print(tag['href'])
        return tag


    def fix_html(self, text):
    
        def has_children(tag):
            children = []
            try:
                tag.children
                children = [x for x in tag.children]
            except:
                pass
            return children

        if not text:
            return ''
        
        multiline = False
        if '\n' in text:
            multiline = True

        # Make text into HTML...
        text = self.convert(text)
        text = smartypants.smartypants(text) # curly quote it
    
        soup = BeautifulSoup(text, 'lxml')

        if soup.body is not None:
            for tag in soup.descendants:
                if tag.name == 'a':
                    # if element.text == None: # TODO: Drop links that have no text
                    tag = self._fix_link(tag)

            if not multiline:
                if len([x for x in soup.body.children]) == 1 and soup.body.p:
                    # We only have one paragraph, so return the _text only_ from the p
                    return ''.join([str(x) for x in soup.body.p.children])
                else:
                    # We have multiline
                    html_string = ''.join([str(x) for x in soup.html.body.children])
            else:
                html_string = ''.join([str(x) for x in soup.html.body.children])

            return html_string
        else:
            return ''

    def quote_converter(self, string, reverse=False):
        """Takes a string and returns it with dumb quotes, single and double,
        replaced by smart quotes. Accounts for the possibility of HTML tags
        within the string."""

        if string == None:
            return None

        if not isinstance(string, str):
            print('Not a string:')
            print(string)
            exit()
        
        if string == '':
            return string

        if reverse == True:
            string = string.replace('“', '"').replace('”', '"')
            string = string.replace('‘', "'").replace("’", "'")
            return string

        # Find dumb double quotes coming directly after letters or punctuation,
        # and replace them with right double quotes.
        string = re.sub(r'([a-zA-Z0-9.,?!;:\'\"])"', r'\1”', string)
        # Find any remaining dumb double quotes and replace them with
        # left double quotes.
        string = string.replace('"', '“')

        # Follow the same process with dumb/smart single quotes
        string = re.sub(r"([a-zA-Z0-9.,?!;:\"\'])'", r'\1’', string)
        string = string.replace("'", '‘')

        return string

PARSER = GitHubParser()


class MarkdownError(Exception):
    pass



all_list_elements = re.compile(r'- ((?:.*)(?:(?:\n\s{2,4})?(?:.*))*)')


def as_list(md):
    """Returns a string of markdown as a Python list"""
    if not md:
        return []
    return(all_list_elements.findall(md))


def extract_links(md: str):
    forbidden_chars = re.compile(r'^[,.()]*|[.,()/]*$')
    md_links = re.compile(r'(?:\[(.*?)\]\((.*?)\))')
    urls_general = re.compile(
        r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

    _ = []

    text = str(md)
    all_urls = md_links.findall(text)
    for i, data in enumerate(all_urls):
        text = data[0]
        url = forbidden_chars.sub('', data[1])
        _.append((text, url))
        text = text.replace(f"[{data[0]}]({data[1]})", "")

    text = text.strip()

    for data in urls_general.findall(text):
        if data[0] != '':
            url = forbidden_chars.sub('', data[0])
            if not url in [x[1] for x in _]:
                _.append(('', url))

    return(_)


def split_into_sections(markdown: str, level_granularity=3, keep_levels=False, clear_empty_lines=True) -> dict:
    """
    Splits a markdown file into a dictionary with the headings as keys and the section contents as values, and returns the dictionary.
    Takes two arguments:
        - level_granularity that can be set to 1, 2, or 3, determining the depth of search for children
        - keep_level which maintains the number of octothorps before the header
    """

    if not isinstance(markdown, str):
        raise MarkdownError(f'Markdown is not string but {type(markdown)}:', markdown) from None
    if clear_empty_lines:
        # cleans out any empty lines
        lines = [_ for _ in markdown.splitlines() if _]
    else:
        lines = markdown.splitlines()

    sections = OrderedDict()

    def is_header(line: str, granularity=level_granularity):
        if granularity == 1:
            if line.startswith("# "):
                return(True)
        elif granularity == 2:
            if line.startswith("# ") or line.startswith("## "):
                return(True)
        elif granularity == 3:
            if line.startswith("# ") or line.startswith("## ") or line.startswith("### "):
                return(True)
        return(False)

    in_code = False
    for linenumber, line in enumerate(lines):
        code = line.startswith('```')
        if code == True:
            if in_code == False:
                in_code = True
            elif in_code == True:
                in_code = False

        if is_header(line) and in_code == False:
            header = ''.join([_ for _ in line.split('#') if _]).strip()
            if keep_levels:
                level = line.strip()[:3].count("#")
                header = f"{'#' * level} {header}"

            if header not in sections:
                sections[header] = ''
                skip_ahead = False
                nextline_in_code = False
                for nextline in lines[linenumber + 1:]:
                    nextline_code = nextline.startswith('```')
                    if nextline_code == True:
                        if nextline_in_code == False:
                            nextline_in_code = True
                        elif nextline_in_code == True:
                            nextline_in_code = False
                    if is_header(nextline) and not nextline_in_code:
                        skip_ahead = True
                    if skip_ahead:
                        continue
                    sections[header] += '\n' + nextline
                sections[header] = sections[header].strip()

    return(sections)
