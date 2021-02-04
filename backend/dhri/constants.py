

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
