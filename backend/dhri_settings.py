from backend.dhri.log import Logger
import yaml
from backend.dhri.exceptions import ConstantError
from pathlib import Path
from datetime import timedelta
from itertools import chain
from backend import models
from django.conf import settings
import os

VERSION = '0.7'

AUTO_REPOS = [
    ('command-line', 'v2.0'),
    ('data-literacies', 'v2.0'),
    ('text-analysis', 'v2.0'),
    ('python', 'v2.0'),
    ('html-css', 'v2.0'),
    ('git', 'v2.0'),
]

GLOSSARY_REPO = ('glossary', 'v2.0')
INSTALL_REPO = ('install', 'v2.0')
INSIGHT_REPO = ('insights', 'v2.0')

# A list of URLs that will not be downloaded by the webcache
DO_NOT_DOWNLOAD = [
    'https://media.githubusercontent.com/media/metmuseum/openaccess/master/MetObjects.csv'
]

AUTO_GROUPS = {
    'Team': {
        models.Profile: ['add', 'change', 'delete', 'view'],

        models.Frontmatter: ['add', 'change', 'delete', 'view'],
        models.LearningObjective: ['add', 'change', 'delete', 'view'],
        models.EthicalConsideration: ['add', 'change', 'delete', 'view'],
        models.Contributor: ['add', 'change', 'delete', 'view'],

        models.Resource: ['add', 'change', 'delete', 'view'],
        #models.Tutorial: ['add', 'change', 'delete', 'view'],
        #models.Project: ['add', 'change', 'delete', 'view'],
        #models.Resource: ['add', 'change', 'delete', 'view'],
        #models.Reading: ['add', 'change', 'delete', 'view'],
        models.Praxis: ['add', 'change', 'delete', 'view'],
        models.Workshop: ['add', 'change', 'delete', 'view'],
    },

    'Learner': {

    },

    'Instructor': {

    }
}


##### Standard settings ##############################

# Where user info is stored:
USER_SETUP = os.path.join(settings.BASE_DIR, 'backend', 'setup', 'users.yml')

# Where snippet info is stored:
SNIPPET_SETUP = os.path.join(settings.BASE_DIR, 'backend', 'setup', 'snippets.yml')

BACKEND_AUTO = 'Github'
REPO_AUTO = ''
BRANCH_AUTO = 'v2.0'

# Set the automatic and maximum size for terminal output
MAX_TERMINAL_WIDTH = 140
AUTO_TERMINAL_WIDTH = 70

# Auto replacement in titles
REPLACEMENTS = {
    '-': ' ',
    'Html Css': 'HTML/CSS',
}

##### Cache ##############################

# .loader-cache/parser/ # TODO: #362 Fix documentation: it's good to keep all of the below in a unique directory on the hard drive and not inside the django-app repo...
CACHE_DIRS = {
    'ROOT': '/tmp/.loader-cache/',
    'PARSER': '/tmp/.gh-api-cache/',
    'WEB': '/tmp/.loader-cache/web/',
    'ZOTERO': '/tmp/.loader-cache/zotero/'
}
IMAGE_CACHE = {
    'INSTALL': '/tmp/.loader-cache/images/install'
}

# The following are written as days
TEST_AGES = {
    'ROOT': 14,
    'PARSER': 14,
    'WEB': 14,
    'ZOTERO': 14,
    'GLOSSARY': 14,
    'INSTALL': 14,
    'INSIGHT': 14
}

# If set to True, the script will override the cache every time (effectively disregarding TEST_AGES above)
FORCE_DOWNLOAD = False


##### Dev features ##############################

# If VERBOSE is set to True, every output message will display the source module/function (good for troubleshooting)
VERBOSE = True
# Note: this outputs a message for each cache age check = generates a LOT of output
CACHE_VERBOSE = False


NORMALIZING_SECTIONS = {
    'frontmatter': {
        'abstract': ['Abstract'],
        'learning_objectives': ['Learning Objectives'],
        'estimated_time': ['Estimated time'],
        'contributors': ['Acknowledgements', 'Acknowledgement', 'Collaborator', 'Collaborators'],
        'ethical_considerations': ['Ethical consideration', 'Ethical considerations', 'Ethics'],
        'readings': ['Pre-reading suggestions', 'Prereading suggestions', 'Pre reading suggestions', 'Pre-readings', 'Pre readings', 'Prereadings', 'Pre-reading', 'Pre reading', 'Prereading'],
        'projects': ['Project', 'Projects', 'Projects that use these skills', 'Projects which use these skills'],
        'prerequisites': ['Prerequisites', 'Pre-requisites', 'Prerequisite', 'Pre-requisite', 'Pre requisites', 'Pre requisite']
    },
    'theory-to-practice': {
        'intro': ['Theory to Practice'],
        'discussion_questions': ['Discussion Questions', 'Discussion Question'],
        'tutorials': ['Other Tutorials', 'More Tutorials', 'Further Tutorials'],
        'further_projects': ['Projects or Challenges to Try', 'Projects to Try', 'Challenges to Try'],
        'further_readings': ['Suggested Further Readings', 'Further Readings', 'Suggested Further Reading', 'Further Reading'],
        'next_steps': ['Next Steps', 'Next Step'],
    },
    'assessment': {
        'qualitative_assessment': ['Qualitative Self-Assessment'],
        'quantitative_assessment': ['Quantitative Self-Assessment'],
    }
}

REQUIRED_SECTIONS = {
    'frontmatter': set(NORMALIZING_SECTIONS['frontmatter'].keys()),
    'theory-to-practice': set(NORMALIZING_SECTIONS['theory-to-practice'].keys()),
    'assessment': set(NORMALIZING_SECTIONS['assessment'].keys())
}

LESSON_TRANSPOSITIONS = {
    '<!-- context: terminal -->': '<img src="terminal.png" />'
}

STATIC_IMAGES = {
    'LESSONS': os.path.join(settings.BASE_DIR, 'website/static/website/images/lessons/'),
    'INSTALL': os.path.join(settings.BASE_DIR, 'media/installation_screenshots/'),
    'INSIGHT': os.path.join(settings.BASE_DIR, 'insight/static/insight/images/'),
    'WORKSHOP_HEADERS': os.path.join(settings.BASE_DIR, 'website/static/website/images/workshop_headers/'),
    'SOFTWARE_HEADERS': os.path.join(settings.BASE_DIR, 'website/static/website/images/software_headers/')
}


# MAKE NO CHANGES BELOW

log = Logger(path=__name__)


for cat in STATIC_IMAGES:
    STATIC_IMAGES[cat] = Path(STATIC_IMAGES[cat])


def _check_normalizer(dictionary=NORMALIZING_SECTIONS):
    for section in NORMALIZING_SECTIONS:
        all_ = [x.lower() for x in list(chain.from_iterable(
            [x for x in NORMALIZING_SECTIONS[section].values()]))]

        if max([all_.count(x) for x in set(all_)]) > 1:
            raise ConstantError(
                'NORMALIZING_SECTIONS is confusing: multiple alternative strings for normalizing.')

    return(True)


for DIR in CACHE_DIRS:
    CACHE_DIRS[DIR] = Path(CACHE_DIRS[DIR])
    if not CACHE_DIRS[DIR].exists():
        CACHE_DIRS[DIR].mkdir()

TEST_AGES['ROOT'] = timedelta(days=TEST_AGES['ROOT'])
TEST_AGES['PARSER'] = timedelta(days=TEST_AGES['PARSER'])
TEST_AGES['WEB'] = timedelta(days=TEST_AGES['WEB'])
TEST_AGES['ZOTERO'] = timedelta(days=TEST_AGES['ZOTERO'])
TEST_AGES['GLOSSARY'] = timedelta(days=TEST_AGES['GLOSSARY'])
TEST_AGES['INSTALL'] = timedelta(days=TEST_AGES['INSTALL'])
TEST_AGES['INSIGHT'] = timedelta(days=TEST_AGES['INSIGHT'])

# Run tests

_check_normalizer()




saved_prefix = '----> '


AUTO_USERS = dict()
try:
    with open(USER_SETUP, 'r') as f:
        AUTO_USERS = yaml.safe_load(f)
except FileNotFoundError:
    log.error(f'Cannot open {USER_SETUP} to read the automatic user information. Make sure your `dhri_settings.py` file contains the correct filename. This means that the script will skip the user setup. Run `manage.py createsuperuser` to be able to access the backend.')
except yaml.parser.ParserError as e:
    log.error(
        f'Cannot parse file {USER_SETUP}. This means that the script will skip the user setup. Run `manage.py createsuperuser` to be able to access the backend. The full error was: {e}')
except yaml.scanner.ScannerError as e:
    log.error(
        f'Cannot parse file {USER_SETUP}. This means that the script will skip the user setup. Run `manage.py createsuperuser` to be able to access the backend. The full error was: {e}')

AUTO_SNIPPETS = dict()
try:
    with open(SNIPPET_SETUP, 'r') as f:
        AUTO_SNIPPETS = yaml.safe_load(f)
except FileNotFoundError:
    log.error(f'Cannot open {SNIPPET_SETUP} to read the automatic snippet information. This means that the script will skip the snippet setup. Make sure your `dhri_settings.py` file contains the correct filename.')
except yaml.parser.ParserError as e:
    log.error(
        f'Cannot parse file {SNIPPET_SETUP}. This means that the script will skip the snippet setup. The full error message was: {e}')
except yaml.scanner.ScannerError as e:
    log.error(
        f'Cannot parse file {SNIPPET_SETUP}. This means that the script will skip the snippet setup. The full error message was: {e}')

REQUIRED_IN_USERS = ['first_name', 'last_name', 'username', 'password']
# AUTO_USERS testing data
AUTO_USER_DEFAULT = AUTO_USERS.get('default')
AUTO_USERS = AUTO_USERS.get('by_groups')
for cat in AUTO_USERS:
    for u in AUTO_USERS[cat]:
        for section in REQUIRED_IN_USERS:
            if not u.get(section):
                log.error(
                    f'User setup file does not contain section `{section}` (in user with username `{u.get("username")}`). Make sure all the users in the `{USER_SETUP}` file contains all the required sections: `{"`, `".join(REQUIRED_IN_USERS)}`.')

for _, dir in IMAGE_CACHE.items():
    IMAGE_CACHE[_] = Path(dir)
    if not IMAGE_CACHE[_].exists():
        IMAGE_CACHE[_].mkdir(parents=True)
