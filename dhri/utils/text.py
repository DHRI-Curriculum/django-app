# General text tools
from dhri.utils.regex import re, URL, NUMBERS, MARKDOWN_HREF, COMPLEX_SEARCH_FOR_URLS


def get_urls(markdown:str) -> list:
    """ Returns a list of URLs in a given string """
    g = re.findall(COMPLEX_SEARCH_FOR_URLS, markdown) # used to be MARKDOWN_HREF (but that's included in COMPLEX_SEARCH_FOR_URLS now)
    return(list(set([x[0] for x in g if x[0]])))


def get_markdown_hrefs(markdown:str) -> list:
    """ Returns a list of URLs in a given string """
    g = re.findall(MARKDOWN_HREF, markdown) # used to be  (but that's included in COMPLEX_SEARCH_FOR_URLS now)
    return(list(set([x for x in g if x]))) # returns unique


def get_number(markdown:str) -> int:
    """ Finds the first number that occurs in a markdown string and
    returns it as integer (removes any decimals for doubles) """
    g = re.search(NUMBERS, markdown)
    if g:
        if '.' in g.groups()[0]:
            assumed_integer = g.groups()[0].split('.')[0]
        else:
            assumed_integer = g.groups()[0]
    else:
        assumed_integer = 0
    return(assumed_integer)
