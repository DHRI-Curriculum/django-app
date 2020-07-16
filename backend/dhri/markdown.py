"""

## Utilities for processing markdown

Overview:
    clear_emptylines(markdown)          Returns markdown string without all empty lines removed.
    lines_as_list(markdown)             Returns a list of each line of the markdown as a list element.
                                            `clean`   indicates whether to pass markdown through
                                                      clean_emptylines() first [bool, default True]
    has_multiline_item(markdown)        Returns bool showing whether markdown has multiline elements.
    is_exclusively_bullets(markdown)    Returns bool showing whether markdown contains *only* bulletpoints.
    get_list(markdown)                  Returns a list of all elements of a kind from a markdown string.
    get_bulletpoints(markdown)          Returns a list of all bulletpoints from a markdown string.
    split_into_sections                 Splits a markdown file into a dictionary with headings as keys
                                        and the section contents as values, and returns as dictionary.
"""

import re
from backend.dhri.regex import MULTILINE_ITEM, ALL_BULLETS, md_links, urls_general
from backend.dhri.log import Logger
from collections import OrderedDict

LIST_ELEMENTS = r'- ((?:.*)(?:(?:\n\s{2,4})?(?:.*))*)'
all_list_elements = re.compile(LIST_ELEMENTS)


def as_list(md):
    """Returns a string of markdown as a Python list"""
    if not md: return []
    return(all_list_elements.findall(md))


def extract_links(md:str):
    FORBIDDEN_URL = r'^[,.()]*|[.,()/]*$'
    forbidden_chars = re.compile(FORBIDDEN_URL)

    _ = []

    text = str(md)
    all_urls = md_links.findall(text)
    for i, data in enumerate(all_urls):
        text = data[0]
        url = forbidden_chars.sub('', data[1])
        _.append((text, url))
        text = text.replace(f"[{data[0]}]({data[1]})","")

    text = text.strip()

    for data in urls_general.findall(text):
        if data[0] != '':
            url = forbidden_chars.sub('', data[0])
            if not url in [x[1] for x in _]: _.append(('', url))

    return(_)



class Markdown():

    class MarkdownIterator:

        def __init__(self, as_list):
            self.as_list = as_list
            self._index = 0

        def __next__(self):
            if self._index <= len(self.as_list)-1:
                _ = self.as_list[self._index]
                self._index += 1
                return _
            raise StopIteration


    log = Logger(name='markdown-interpreter')

    def __init__(self, *args, **kwargs) -> None:
        self.verbose = False

        if 'text' in kwargs:
            self.raw_text = kwargs['text']
        elif len(args) == 1:
            self.raw_text = args[0]

        self.raw_text = self._pre_process()

        self._links = []

    def _pre_process(self):
        if isinstance(self.raw_text, str):
            newlines = []
            for line in self.raw_text.splitlines():
                if line == '':
                    continue
                if line.strip().startswith('-'): # cannot handle nested lists right now
                    newlines.append(line.strip())
                    continue
                else:
                    newlines.append(line)
            return("\n".join(newlines))
        return(self.raw_text)

    def as_list(self):
        """Returns the raw markdown as a python list for iteration but disregards any extra text"""
        as_list = all_list_elements.findall(self.raw_text) # has each line in a tuple
        return([Markdown(text=f'{x[0]}\n{x[1]}'.strip()) for x in as_list])

    def _find_links(self):
        FORBIDDEN_URL = r'^[,.()]*|[.,()/]*$'
        forbidden_chars = re.compile(FORBIDDEN_URL)

        _ = []

        text = str(self.raw_text)
        all_urls = md_links.findall(text)
        for i, data in enumerate(all_urls):
            text = data[0]
            url = forbidden_chars.sub('', data[1])
            _.append((text, url))
            text = text.replace(f"[{data[0]}]({data[1]})","")

        text = text.strip()

        for data in urls_general.findall(text):
            if data[0] != '':
                url = forbidden_chars.sub('', data[0])
                if not url in [x[1] for x in _]: _.append(('', url))

        return(_)


    @property
    def bulletpoints(self):
        return(len([x for x in self.raw_text.splitlines() if x.strip().startswith('-')]))

    @property
    def is_only_bulletpoints(self):
        is_only_bulletpoints = re.sub(ALL_BULLETS, "", self.raw_text) == ''
        if self.verbose:
            if is_only_bulletpoints == False:
                log.warning(f'Markdown does not only contain bulletpoints: {self.linecount} lines but {self.bulletpoints} bulletpoints.')
        return is_only_bulletpoints

    @property
    def linecount(self):
        return(len(self.raw_text.splitlines()))

    @property
    def links(self):
        if not self._links:
            self._links = self._find_links()
        return(self._links)

    @property
    def has_links(self):
        return len(self.links) > 0

    @property
    def has_multiple_links(self):
        return len(self.links) > 1

    def __iter__(self):
        return(self.MarkdownIterator(self.as_list()))

    def __str__(self):
        return(str(self.raw_text))

    @property
    def no_link(self):
        text = self.raw_text
        text = md_links.sub("", text)
        text = urls_general.sub("", text)
        text = text.strip()
        return(text)

    @property
    def one_line(self):
        return(self.raw_text.replace("\n", " "))

    def as_contributors(self):
        as_list = [Markdown(text=x) for x in self.as_list()]
        separate_role = re.compile(r':\s')
        _ = []
        for line in as_list:
            name, link, role = '', '', ''

            if separate_role.findall(str(line)):
                role, names = separate_role.split(str(line))
                for name in names.split(','):
                    name = name.strip()
                    if not name or name.lower().strip() == 'none':
                        log.warning("Found a contributor with no name — skipping.")
                        continue
                    as_md = Markdown(text=name)
                    if as_md.links:
                        name = as_md.links[0][0]
                        link = as_md.links[0][1]
                    first_name, last_name = split_names(name)
                    _.append((first_name, last_name, role, link))
                continue
            else:
                if line.links:
                    name = line.links[0][0]
                    link = line.links[0][1]
                else:
                    name = str(line)
            first_name, last_name = split_names(name)
            if not first_name or not last_name or name.lower().strip() == 'none':
                log.warning("Found a contributor with no name — skipping.")
                continue
            _.append((first_name, last_name, role, link))
        return(_)


log = Logger(name="markdown")

def clear_emptylines(markdown:str) -> str:
    """ Returns markdown string without all empty lines removed """
    return "\n".join([x for x in markdown.splitlines() if x])


def lines_as_list(markdown:str, clean_emptylines=True) -> list:
    """ Returns a list of each line of the markdown as a list element. Takes one argument, `clean` (bool, default True) which indicates whether to pass markdown through clean_emptylines first. """
    if clean_emptylines: return(clear_emptylines(markdown).splitlines())
    return markdown.splitlines()


def has_multiline_item(markdown:str) -> bool:
    """ Returns bool showing whether markdown has multiline elements """
    if re.search(MULTILINE_ITEM, markdown): return(True)
    return False


def is_exclusively_bullets(markdown:str) -> bool:
    """ Returns bool showing whether markdown contains exclusively bulletpoints (incl. multi-line ones) """
    return re.sub(ALL_BULLETS, "", markdown) == ''


def get_list(markdown:str, *args) -> list:
    """
    Returns a list of all elements of a kind from a markdown string.
    Accepts one extra argument: which regex to extract (default=ALL_BULLETS).
        Aliases exist for:
            ALL_BULLETS: All bulletpoints in markdown
            ALL_LISTS: All numbered lists in markdown
            BULLETS_EXTRA_P: All bulletpoints in markdown that have an extra paragraph
            BULLETS_NO_EXTRA_P: All bulletpoints in markdown that do not have an extra paragraph
    """
    if not len(args):
        _regex = ALL_BULLETS
    else:
        _regex = args[0]
    try:
        return(re.findall(_regex, markdown, re.MULTILINE))
    except TypeError:
        log.error(f"Cannot interpret the text {markdown}", raise_error=TypeError)


def get_bulletpoints(markdown:str) -> list:
    """
    Returns a list of all bulletpoints from a markdown string.
    [Alias function for get_list(markdown, ALL_BULLETS).]
    """
    return(get_list(markdown, ALL_BULLETS))


def split_into_sections(markdown:str, level_granularity=3, keep_levels=False, clear_empty_lines=True) -> dict:
    """
    Splits a markdown file into a dictionary with the headings as keys and the section contents as values, and returns the dictionary.
    Takes two arguments:
      - level_granularity that can be set to 1, 2, or 3, determining the depth of search for children
      - keep_level which maintains the number of octothorps before the header
    """

    if clear_empty_lines:
        lines = [_ for _ in markdown.splitlines() if _] # cleans out any empty lines
    else:
        lines = markdown.splitlines()

    sections = OrderedDict()

    def is_header(line:str, granularity=level_granularity):
        if granularity == 1:
            if line.startswith("# "): return(True)
        elif granularity == 2:
            if line.startswith("# ") or line.startswith("## "): return(True)
        elif granularity == 3:
            if line.startswith("# ") or line.startswith("## ") or line.startswith("### "): return(True)
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
                    if is_header(nextline) and not nextline_in_code: skip_ahead = True
                    if skip_ahead: continue
                    sections[header] += '\n' + nextline
                sections[header] = sections[header].strip()

    return(sections)



def destructure_list(markdown:str, remove_simple_links=True, set_empty_url='') -> list:
    """Takes a markdown string and destructures it into a list consisting of
    its list elements (marked by "- " in markdown).

    Then it searches each list element for links, either hard coded urls or
    markdown links (marked by "[text](url)" in markdown).

    Returns a list of a tuple with two values from each list element:
        1. the text from the list element
        2. a list of tuples:
             1. text used to link using markdown
             2. the raw URL occurring in the link

    Note: disregards any lines in the markdown that are not list elements,
    and does not create a warning for doing so.

    ######## Example #####################################

    markdown.md:
        Here is a paragraph.
        - here is a list element
        - here is another list element with two raw URLs: http://www.apple.com and https://www.microsoft.com
        - here is another list element
        - and a fifth with a [link](http://www.apple.com) and [link](http://www.microsoft.com)

    output from running this text through destructure_list(markdown):
        [
            (
                'here is a list element',
                []
            ),
            (
                'here is another list element with two raw URLs: http://www.apple.com and https://www.microsoft.com',
                [(
                    '',
                    'http://www.apple.com'
                ),
                (
                    '',
                    'https://www.microsoft.com'
                )]
            ),
            (
                'here is another list element',
                []
            ),
            (
                'and a fifth with a [link](http://www.apple.com) and [link](http://www.microsoft.com)',
                [(
                    'link',
                    'http://www.apple.com'
                ),
                (
                    'link',
                    'http://www.microsoft.com'
                )]
            )
        ]

    """

    if not isinstance(markdown, str):
        log.warning(f'List is not provided as string but as {type(markdown)}. Trying to fix.')
        markdown = _fix_markdown(markdown, type="")

    from dhri.utils.regex import is_md_link, md_list, all_links

    _ = []
    for list_element in md_list.findall(markdown):
        text, link = list_element, set_empty_url
        urls = []
        for url in all_links.findall(list_element):
            full_match, text, link = url
            if is_md_link.match(full_match) == None:
                link = full_match
                text = ''
            else:
                text, link = is_md_link.match(full_match).groups()
            urls.append((text, link))
            continue
        if link != '':
            pass # do something with link
        if list_element == text: text = ''
        _.append((list_element, urls))
    return(_)



def split_names(full_name:str) -> tuple:
    """Uses the `nameparser` library to interpret names."""

    from nameparser import HumanName

    name = HumanName(full_name)
    first_name = name.first
    if name.middle:
        first_name += " " + name.middle
    last_name = name.last
    return((first_name, last_name))

def _fix_markdown(markdown, type="") -> str:
    new_markdown = ""
    if isinstance(markdown, list):
        for item in markdown:
            if isinstance(item, str):
                if item != '': new_markdown += "- " + item + "\n"
            elif isinstance(item, tuple):
                for c in item:
                    if c != '': new_markdown += "- " + c + "\n"
            else:
                log.warning(f'Could not fix. Please fix the {type} list for the repository.')
    else:
        log.warning(f'Could not fix. Please fix the {type} list for the repository.')
    return new_markdown


def get_contributors(markdown:str) -> list:
    """Parses a list of contributors and returns a list of tuples. Each tuple contains the following information:
          1. first_name
          2. last_name
          3. role (optional, if not present an empty string)
          4. link (optional, if not present an empty string)
    """

    if not isinstance(markdown, str):
        log.warning(f'Contributors are not provided as string but as {type(markdown)}. Trying to fix.')
        markdown = _fix_markdown(markdown, type="contributor")

    _, collected = [], []

    for person, links in destructure_list(markdown):
        link, role = '', ''
        if ": " in person:
            role, person = person.split(": ")[0], "".join([x for x in person.split(": ")[1:] if x])
        if person == '' or person == 'none':
            log.warning(f'List of contributors contains a person with no name with role set to "{role}". Skipping this person.')
            continue
        if "," in person:
            person_split = person.split(", ")
        else:
            person_split = [person]

        for person in person_split:
            link = ''
            if links:
                for person_test, link_test in links:
                    if not person_test == '': person = person_test
                    if not link_test == '': link = link_test

            first_name, last_name = split_names(person)

            if not (person, role) in collected:
                _.append((first_name, last_name, role, link))
                collected.append((person, role))
            else:
                log.warning('Contributors contain multiple occurrences of the same person in the same role. Will skip.')

    return(_)