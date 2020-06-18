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

"""

import re

MULTILINE_ITEM = r"\s{3,10}"
HAS_BULLETPOINTS = r"\n?-"
GET_BULLETPOINTS = {
    'ALL': r'\n?- (.*)(?:(?=\s{2,8})\s{2,8}(.*))?',
    'THOSE_WITH_EXTRA_PARAGRAPH': r'\n?- (.*)\n(?=  )\s+(.*)\n?',
    'THOSE_WITH_NO_EXTRA_PARAGRAPH': r'\n?- (.*)\n(?!  )'
}
GET_NUMBERED_LISTS = {
    'ALL': r'\n?[1-9]\. (.*)(?>(?=\s{2,8})\s{2,8}(.*))?',
}
GET_QUESTIONS = {
    'ALL': r'', # TODO: this one is hard for my head right now
    'ONLY_QUESTIONS': r'\n|^(?(?!- ).*)',
    'ONLY_ANSWERS': r'\n|^(?(?=- ).*)',
}

ALL_BULLETS = GET_BULLETPOINTS['ALL']
BULLETS_EXTRA_P = GET_BULLETPOINTS['THOSE_WITH_EXTRA_PARAGRAPH']
BULLETS_NO_EXTRA_P = GET_BULLETPOINTS['THOSE_WITH_NO_EXTRA_PARAGRAPH']
ALL_NUMBERS = GET_NUMBERED_LISTS['ALL']


def clear_emptylines(markdown:str) -> str:
    """ Returns markdown string without all empty lines removed """
    return "\n".join([x for x in markdown.splitlines() if x])


def lines_as_list(markdown:str, clean_emptylines=True) -> list:
    """ Returns a list of each line of the markdown as a list element. Takes one argument, `clean` (bool, default True) which indicates whether to pass markdown through clean_emptylines first. """
    if clean_emptylines: return(clear_emptylines(markdown).splitlines())
    return markdown.splitlines()


def has_multiline_item(markdown:str) -> bool:
    """ Returns bool showing whether markdown has multiline elements """
    # TODO: replaces test_markdown_for_multiline()
    if re.search(MULTILINE_ITEM, markdown): return(True)
    return False


def is_exclusively_bullets(markdown:str) -> bool:
    """ Returns bool showing whether markdown contains exclusively bulletpoints (incl. multi-line ones) """
    # TODO: replaces section_is_bulletpoints()
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
        _regex = GET_BULLETPOINTS['ALL_BULLETS']
    else:
        _regex = args[0]
    return(re.findall(_regex, markdown, re.MULTILINE))


def get_bulletpoints(markdown:str) -> list:
    """ 
    Returns a list of all bulletpoints from a markdown string.
    [Alias function for get_list(markdown, ALL_BULLETS).]
    """
    return(get_list(markdown, GET_BULLETPOINTS['ALL']))


def split_into_sections(markdown:str) -> dict:
    """
    Splits a markdown file into a dictionary with the headings as keys and the section contents as values, and returns the dictionary.
    """

    lines = [x for x in markdown.splitlines() if x] # cleans out any empty lines

    sections = {}

    for linenumber, line in enumerate(lines):
        if line.startswith('### ') or line.startswith('## ') or line.startswith('# '):
            header = ''.join([x for x in line.split('#') if x]).strip()
            if header not in sections:
                sections[header] = ''
                skip_ahead = False
                for nextline in lines[linenumber + 1:]:
                    if nextline.startswith('#'): skip_ahead = True
                    if skip_ahead: continue
                    sections[header] += '\n' + nextline
                sections[header] = sections[header].strip()

                if is_exclusively_bullets(sections[header]):
                    sections[header] = get_bulletpoints(sections[header])
                else:
                    sections[header] = clear_emptylines(sections[header])

    return(sections)
