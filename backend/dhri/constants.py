

def get_replacements():
    from backend.dhri_settings import REPLACEMENTS
    return REPLACEMENTS

def get_regex(selector='NUMBERS'):
    from backend.dhri.regex import NUMBERS, MARKDOWN_HREF, COMPLEX_SEARCH_FOR_URLS

    if selector == 'NUMBERS':
        return NUMBERS
    elif selector == 'MARKDOWN_HREF':
        return MARKDOWN_HREF
    elif selector == 'COMPLEX_SEARCH_FOR_URLS':
        return COMPLEX_SEARCH_FOR_URLS

def get_verbose():
    from backend.dhri_settings import VERBOSE
    return VERBOSE

def get_terminal_width():
    from backend.dhri_settings import AUTO_TERMINAL_WIDTH, MAX_TERMINAL_WIDTH
    import os

    try:
        TERMINAL_WIDTH = os.popen('stty size', 'r').read().split()[1]
        TERMINAL_WIDTH = int(TERMINAL_WIDTH)
    except:
        TERMINAL_WIDTH = AUTO_TERMINAL_WIDTH

    if TERMINAL_WIDTH > MAX_TERMINAL_WIDTH:
        TERMINAL_WIDTH = MAX_TERMINAL_WIDTH

    return TERMINAL_WIDTH


def get_saved_prefix():
    from backend.dhri_settings import saved_prefix
    return saved_prefix