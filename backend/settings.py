from django.conf import settings
from django.apps import apps
from backend.logger import Logger

from app.secrets import SECRET_KEY, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, GITHUB_TOKEN, ZOTERO_KEY

import datetime
import itertools
import os
import pathlib
import yaml

BASE_DIR = settings.BASE_DIR
BUILD_DIR = f'{BASE_DIR}/_preload/'

def get_all_models():
    all_apps = [x.split('.')[0] for x in settings.INSTALLED_APPS if not x.startswith(
        'django') and '.apps.' in x]
    _ = [apps.all_models[x] for x in all_apps]
    all_models = list()
    [all_models.extend(list(x.values())) for x in _]
    all_models = {model.__name__: model for model in all_models}
    return all_models

all_models = get_all_models()

SETUP_DIR = os.path.join(settings.BASE_DIR, 'backend', 'setup')
if not os.path.exists(SETUP_DIR):
    exit('Required setup directory does not exist: ' + SETUP_DIR)

SETUP_FILES = {
    # User settings file
    'users.yml': os.path.join(SETUP_DIR, 'users.yml'),

    # Groups settings file
    'groups.yml': os.path.join(SETUP_DIR, 'groups.yml'),

    # Snippet settings file
    'snippets.yml': os.path.join(SETUP_DIR, 'snippets.yml'),

    # Repositories settings file
    'repositories.yml': os.path.join(SETUP_DIR, 'repositories.yml'),

    # UX settings file
    'ux.yml': os.path.join(SETUP_DIR, 'ux.yml'),

    # Backend settings file
    'backend.yml': os.path.join(SETUP_DIR, 'backend.yml'),

    # Content transformation settings file
    'content-transform.yml': os.path.join(SETUP_DIR, 'content-transform.yml')
}
for path in SETUP_FILES.values():
    if not os.path.exists(path):
        exit('Required settings file does not exist: ' + path)

def get_settings(SETUP_FILES=SETUP_FILES):
    SETUP = {}
    for file, path in SETUP_FILES.items():
        try:
            with open(path, 'r') as f:
                SETUP[file] = yaml.safe_load(f)
        except FileNotFoundError:
            exit(
                'Required settings file {file} could not be found in the correct path ({path}). Before the script can run, the correct settings must be in the right place.')
    return SETUP

SETUP = get_settings()

# Initiate logger
log = Logger(path=__name__)

# Correcting
# 1. Setup tuples for AUTO_REPOS, GLOSSARY_REPO, INSTALL_REPO, INSIGHT_REPO
AUTO_REPOS = [(x['repo'], x['branch'])
              for x in SETUP['repositories.yml']['workshops']]

GLOSSARY_REPO = (SETUP['repositories.yml']['meta']['glossary']['repo'],
                 SETUP['repositories.yml']['meta']['glossary']['branch'])
INSTALL_REPO = (SETUP['repositories.yml']['meta']['install']['repo'],
                SETUP['repositories.yml']['meta']['install']['branch'])
INSIGHT_REPO = (SETUP['repositories.yml']['meta']['insight']['repo'],
                SETUP['repositories.yml']['meta']['insight']['branch'])

# 2. Make sure all types are correct
SETUP['backend.yml']['STATIC_IMAGES'] = {key: value.replace('$BASE_DIR', settings.BASE_DIR)
                 for key, value in SETUP['backend.yml']['STATIC_IMAGES'].items()}
SETUP['backend.yml']['STATIC_IMAGES'] = {key: pathlib.Path(value) for key, value in SETUP['backend.yml']['STATIC_IMAGES'].items()}
SETUP['backend.yml']['CACHE_DIRS'] = {key: value.replace('$BASE_DIR', settings.BASE_DIR)
                 for key, value in SETUP['backend.yml']['CACHE_DIRS'].items()}
SETUP['backend.yml']['TEST_AGES'] = {key: datetime.timedelta(days=value) for key, value in SETUP['backend.yml']['TEST_AGES'].items()}

_SETUP = {'groups.yml': {}}
for group, data in SETUP['groups.yml'].items():
    _SETUP['groups.yml'][group] = {}
    for model, permissions in data.items():
        _SETUP['groups.yml'][group][all_models[model]] = permissions
SETUP['groups.yml'] = _SETUP['groups.yml']


# Setting up shortcuts
VERSION = SETUP['backend.yml']['VERSION']
CACHE_DIRS = SETUP['backend.yml']['CACHE_DIRS']
IMAGE_CACHE = SETUP['backend.yml']['IMAGE_CACHE']
STATIC_IMAGES = SETUP['backend.yml']['STATIC_IMAGES']
TEST_AGES = SETUP['backend.yml']['TEST_AGES']
FORCE_DOWNLOAD = SETUP['backend.yml']['FORCE_DOWNLOAD']
VERBOSE = SETUP['backend.yml']['VERBOSE']
CACHE_VERBOSE = SETUP['backend.yml']['CACHE_VERBOSE']
DO_NOT_DOWNLOAD = SETUP['backend.yml']['DO_NOT_DOWNLOAD']
BACKEND_AUTO = SETUP['repositories.yml']['backend']
MAX_TERMINAL_WIDTH = SETUP['ux.yml']['terminal_width']['max']
AUTO_TERMINAL_WIDTH = SETUP['ux.yml']['terminal_width']['auto']
NORMALIZING_SECTIONS = SETUP['content-transform.yml']['NORMALIZING_SECTIONS']
LESSON_TRANSPOSITIONS = SETUP['content-transform.yml']['LESSON_TRANSPOSITIONS']
AUTO_GROUPS = SETUP['groups.yml']
AUTO_USER_DEFAULT = SETUP['users.yml']['default']
AUTO_USERS = SETUP['users.yml']['by_groups']
AUTO_SNIPPETS = SETUP['snippets.yml']

REQUIRED_SECTIONS = {
    'frontmatter': set(NORMALIZING_SECTIONS['frontmatter'].keys()),
    'theory-to-practice': set(NORMALIZING_SECTIONS['theory-to-practice'].keys())
}

# Run tests
def _check_normalizer(NORMALIZING_SECTIONS=NORMALIZING_SECTIONS, log=log):
    for section in NORMALIZING_SECTIONS:
        all_ = [x.lower() for x in list(itertools.chain.from_iterable(
            [x for x in NORMALIZING_SECTIONS[section].values()]))]

        if max([all_.count(x) for x in set(all_)]) > 1:
            log.error(
                'NORMALIZING_SECTIONS is confusing: multiple alternative strings for normalizing.')

    return True

def _check_dirs_existence(DIRS=CACHE_DIRS):
    for DIR in DIRS:
        DIRS[DIR] = pathlib.Path(DIRS[DIR])
        if not DIRS[DIR].exists():
            DIRS[DIR].mkdir(parents=True)
    return True

def _check_users(REQUIRED_IN_USERS=['first_name', 'last_name', 'username', 'password'], AUTO_USERS=AUTO_USERS):
    for cat, userlist in AUTO_USERS.items():
        for u in userlist:
            for section in REQUIRED_IN_USERS:
                if not u.get(section):
                    log.error(
                        f'User setup file does not contain section `{section}` (in user with username `{u.get("username")}`). Make sure all the users in the `{SETUP_FILES["users.yml"]}` file contains all the required sections: `{"`, `".join(REQUIRED_IN_USERS)}`.')
    return True

if not _check_normalizer():
    log.error('An unknown error occurred while checking for sections in NORMALIZING_SECTIONS.')
if not _check_dirs_existence():
    log.error('An unknown error occurred while ensuring that all cache directories exist.')
if not _check_dirs_existence(DIRS=IMAGE_CACHE):
    log.error('An unknown error occurred while ensuring that all image cache directories exist.')
if not _check_dirs_existence(DIRS=STATIC_IMAGES):
    log.error('An unknown error occurred while ensuring that static image directories exist.')
if not _check_users():
    log.error('An unknown error occurred when ensuring users were correctly created in the settings file.')
