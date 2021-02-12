import re
from django.utils.text import slugify


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
