import requests
from requests.exceptions import HTTPError

from dhri.constants import _test, REMOVE_EMPTY_HEADINGS, BULLETPOINTS_TO_LISTS, BRANCH_AUTO
from dhri.logger import Logger

# TODO: add a constant FORCE_BULLETPOINTS that uses regex to extract whatever bulletpoints exist in a section and skip other content.


log = Logger()

def verify_repo(string):
    """ Verifies that a provided repository string is correct. Returns a string with corrected information """

    # TODO: This function doubles up with verify_url() from .meta

    if string == None:
        log.error('No repository URL provided.', raise_error=RuntimeError)

    if string.endswith('/'):
        string = string[:-1]

    if len(string.split('/')) != 5:
        log.error('Cannot interpret repository URL. Are you sure it is a simple https://github.com/user-name/repo link?', raise_error=RuntimeError)

    return(string)


def get_text_from_url(url):
    """ # TODO: insert docstring here """

    r = requests.get(url)
    
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.error(f'The URL ({url}) could not be used. Verify that you are using the correct repository, and that the branch that you provide is correct.')
    
    return(r.text)


def get_raw_content(repo=None, branch=BRANCH_AUTO):
    """
    Downloads all the raw content from a provided repository on GitHub, and from a particular master.

    The repository must be *public* and must contain the following three files:
    - frontmatter.md
    - theory-to-practice.md
    - assessment.md
    """

    repo = verify_repo(repo)

    user = repo.split('/')[3]
    repo_name = repo.split('/')[4]

    raw_url = f'https://raw.githubusercontent.com/{user}/{repo_name}/{branch}'

    raw_urls = {}
    raw_urls['frontmatter'] = f'{raw_url}/frontmatter.md'
    raw_urls['theory-to-practice'] = f'{raw_url}/theory-to-practice.md'
    raw_urls['assessment'] = f'{raw_url}/assessment.md'

    return({
        'meta': {
            'raw_urls': raw_urls,
            'repo_url': repo,
            'user': user,
            'repo_name': repo_name,
            'branch': branch,
        },
        'content': {
            'frontmatter': get_text_from_url(raw_urls['frontmatter']),
            'theory-to-practice': get_text_from_url(raw_urls['theory-to-practice']),
            'assessment': get_text_from_url(raw_urls['assessment']),
        }
    })


def section_is_bulletpoints(markdown):
    """ Returns `True` if a section of markdown only contains bullet points. Otherwise returns `False` """
    
    # First, make sure there ARE lists in there at all
    if not '\n- ' in markdown and not markdown.startswith('- '):
        return False
    
    num_lines = len(markdown.splitlines())
    num_of_bulletpoint_lines = len([x for x in markdown.splitlines() if x.startswith('- ')])

    return num_of_bulletpoint_lines == num_lines


def section_as_list(markdown, shave_off=2):
    """ Returns each line from a markdown section as a list element, with the first `shave_off` letters removed from each element. """
    return [x[shave_off:] for x in markdown.splitlines()]


def split_md_into_sections(markdown, remove_empty_headings=REMOVE_EMPTY_HEADINGS, bulletpoints_to_lists=BULLETPOINTS_TO_LISTS):
    """
    Splits a markdown file into a dictionary with the headings as keys and the section contents as values, and returns the dictionary.

    The function accepts two arguments:
    - `remove_empty_headings` (bool) which determines whether empty dictionary keys (headings) should be removed from the dictionary (defaults to REMOVE_EMPTY_HEADINGS, defined on line 3)
    - `bulletpoints_to_lists` (bool) which determines whether sections that contain ONLY bulletpoints should be converted into python lists with each bullet point as an element in the list (defaults to BULLETPOINTS_TO_LISTS, defined on line 4)
    """

    _test(variable=remove_empty_headings)
    _test(variable=bulletpoints_to_lists)
    
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

                if bulletpoints_to_lists:
                    if section_is_bulletpoints(sections[header]):
                        sections[header] = section_as_list(sections[header], shave_off=2)

                if remove_empty_headings:
                    if len(sections[header]) == 0: del sections[header]

    return(sections)


def split_md_into_sections_batch(section_names: set, dictionary: dict) -> dict:
    """ Can run multiple split_md_into_sections and return a dictionary with the results """
    _ = {}
    for section_name in section_names:
        if section_name not in _:
            _[section_name] = split_md_into_sections(dictionary[section_name])
    return(_)
