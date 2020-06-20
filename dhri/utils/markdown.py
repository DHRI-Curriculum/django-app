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

from dhri.utils.regex import re, MULTILINE_ITEM, ALL_BULLETS
from dhri.interaction import Logger


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


from nameparser import HumanName

def split_names(full_name:str) -> tuple:
    """Uses the `nameparser` library to interpret names."""
    name = HumanName(full_name)
    first_name = name.first
    if name.middle:
        first_name += " " + name.middle
    last_name = name.last
    return((first_name, last_name))

def _fix_markdown(markdown) -> str:
    new_markdown = ""
    if isinstance(markdown, list):
        for contributor in markdown:
            if isinstance(contributor, str):
                if contributor != '': new_markdown += "- " + contributor + "\n"
            elif isinstance(contributor, tuple):
                for c in contributor:
                    if c != '': new_markdown += "- " + c + "\n"
            else:
                log.warning(f'Could not fix. Please fix the contributor list for the repository.')
    else:
        log.warning(f'Could not fix. Please fix the contributor list for the repository.')
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
        markdown = _fix_markdown(markdown)

    _ = []
    collected = []
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
