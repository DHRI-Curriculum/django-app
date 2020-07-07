REQUIRED_SECTIONS = {}

##################################################################




######## DO NOT EDIT BELOW THIS LINE IF YOU DON'T KNOW WHAT YOU ARE DOING ##############

# Make sure to set up a test of all of the constants

from dhri.interaction import Logger
from dhri.utils.exceptions import ConstantError
from dhri.settings import NORMALIZING_SECTIONS, DOWNLOAD_CACHE_DIR, TEST_AGE, ZOTERO_TEST_AGE, MAX_TERMINAL_WIDTH

from itertools import chain
from datetime import timedelta
from pathlib import Path
import os

log = Logger(name="constants")

def _test(constant=None, as_type=bool):
    if not isinstance(constant, as_type): log.error(f'{constant}` provided must be a {as_type}.', raise_error=ConstantError)
    return(True)

def _check_normalizer(dictionary=NORMALIZING_SECTIONS):
    for section in NORMALIZING_SECTIONS:
        all_ = [x.lower() for x in list(chain.from_iterable([x for x in NORMALIZING_SECTIONS[section].values()]))]

        if max([all_.count(x) for x in set(all_)]) > 1:
            log.error('NORMALIZING_SECTIONS is confusing: multiple alternative strings for normalizing.', raise_error=ConstantError)

    return(True)


DOWNLOAD_CACHE_DIR = Path(DOWNLOAD_CACHE_DIR)
if not DOWNLOAD_CACHE_DIR.exists(): DOWNLOAD_CACHE_DIR.mkdir()

TEST_AGE = timedelta(minutes=TEST_AGE)
TEST_AGE_WEB = timedelta(minutes=5) # Test age for WebCache is set to 30 days.
ZOTERO_TEST_AGE = timedelta(days=ZOTERO_TEST_AGE) # every two days

# Run tests

_check_normalizer()


try:
    TERMINAL_WIDTH = os.popen('stty size', 'r').read().split()[1]
    TERMINAL_WIDTH = int(TERMINAL_WIDTH)
except:
    TERMINAL_WIDTH = 70

if TERMINAL_WIDTH > MAX_TERMINAL_WIDTH: TERMINAL_WIDTH = MAX_TERMINAL_WIDTH
