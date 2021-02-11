import re
from django.utils.text import slugify
from collections import OrderedDict

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
        raise RuntimeError('Markdown is not string:', markdown)
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


def get_terminal_width():
    from backend.settings import AUTO_TERMINAL_WIDTH, MAX_TERMINAL_WIDTH
    import os

    try:
        TERMINAL_WIDTH = os.popen('stty size', 'r').read().split()[1]
        TERMINAL_WIDTH = int(TERMINAL_WIDTH)
    except:
        TERMINAL_WIDTH = AUTO_TERMINAL_WIDTH

    if TERMINAL_WIDTH > MAX_TERMINAL_WIDTH:
        TERMINAL_WIDTH = MAX_TERMINAL_WIDTH

    return TERMINAL_WIDTH


def get_verbose():
    from backend.settings import get_settings
    return get_settings()['backend.yml']['VERBOSE']


def dhri_slugify(string: str) -> str:
    # first replace any non-OK characters [/] with space
    string = re.sub(r'[\/\-\–\—\_]', ' ', string)

    # then replace too many spaces with one space
    string = re.sub(r'\s+', ' ', string)

    # then replace space with -
    string = re.sub(r'\s', '-', string)

    # then replace any characters that are not in ALLOWED charset with nothing
    string = re.sub(r'[^a-zA-Z\-\s]', '', string)

    # finally, use Django's slugify
    string = slugify(string)

    return string
