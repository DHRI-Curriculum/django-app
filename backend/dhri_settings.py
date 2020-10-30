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

AUTO_GROUPS = {
    'Team': {
        models.Profile: ['add', 'change', 'delete', 'view'],

        models.Frontmatter: ['add', 'change', 'delete', 'view'],
        models.LearningObjective: ['add', 'change', 'delete', 'view'],
        models.EthicalConsideration: ['add', 'change', 'delete', 'view'],
        models.Contributor: ['add', 'change', 'delete', 'view'],

        models.Tutorial: ['add', 'change', 'delete', 'view'],
        models.Project: ['add', 'change', 'delete', 'view'],
        models.Resource: ['add', 'change', 'delete', 'view'],
        models.Reading: ['add', 'change', 'delete', 'view'],
        models.Praxis: ['add', 'change', 'delete', 'view'],
        models.Workshop: ['add', 'change', 'delete', 'view'],
    },

    'Learner': {

    },

    'Instructor': {

    }
}


AUTO_PAGES = [
    {
        'name': 'Workshops',
        'slug': 'workshops',
        'text': '<p class="lead">This is the workshop page.</p>',
        'template': 'workshop/workshop-list.html',
    },
    {
        'name': 'Library',
        'slug': 'library',
        'text': '<p class="lead">This is the library page.</p>',
        'template': 'library/index.html',
    },
]

##### Standard settings ##############################

# Where user info is stored:
USER_SETUP = os.path.join(settings.BASE_DIR, '_preload/user_setup.yml')

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

CACHE_DIRS = {
    'ROOT': '.loader-cache/',
    # .loader-cache/parser/ # TODO: For documentation - it's good to keep this in a unique directory on the hard drive...
    'PARSER': '/tmp/.gh-api-cache/',
    'WEB': '.loader-cache/web/',
    'ZOTERO': '.loader-cache/zotero/'
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

IMAGE_CACHE = {
    'INSTALL': '.loader-cache/images/install'
}


##### Dev features ##############################

# If VERBOSE is set to True, every output message will display the source module (good for troubleshooting)
VERBOSE = False


NORMALIZING_SECTIONS = {
    'frontmatter': {
        'abstract': ['Abstract'],
        'learning_objectives': ['Learning Objectives'],
        'estimated_time': ['Estimated time'],
        'contributors': ['Acknowledgements', 'Acknowledgement', 'Collaborator', 'Collaborators'],
        'ethical_considerations': ['Ethical consideration', 'Ethical considerations', 'Ethics'],
        'readings': ['Pre-reading suggestions', 'Prereading suggestions', 'Pre reading suggestions', 'Pre-readings', 'Pre readings', 'Prereadings', 'Pre-reading', 'Pre reading', 'Prereading'],
        'projects': ['Project', 'Projects', 'Projects that use these skills', 'Projects which use these skills'],
        'resources': ['Resources (optional)', 'Resource (optional)', 'Resources optional', 'Resource optional'],
    },
    'theory-to-practice': {
        'intro': ['Theory to Practice'],
        'discussion_questions': ['Discussion Questions'],
        'tutorials': ['Other Tutorials'],
        'further_projects': ['Projects or Challenges to Try'],
        'further_readings': ['Suggested Further Readings'],
        'next_steps': ['Next Steps']
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


# REMOVED FEATURES (So can likely be removed)

# If set to True, resets all the DHRI curriculum database elements automatically before script runs (not recommended in production)
# AUTO_RESET = True # TODO: I believe this isn't in use anymore

# If set to True, the database will be erased and reset for each run
# DEBUG = True # TODO: I believe this isn't in use anymore


# This is where the final fixtures JSON file will be saved
# FIXTURE_PATH = 'app/fixtures.json' # TODO: Remove, after making sure the app works.

'''
# Django backend settings
DJANGO_PATHS = {
        'DJANGO': 'app/',
        'DB': 'app/db.sqlite3',
        'MANAGE': 'app/manage.py',
    }
'''  # TODO: Remove, after making sure the app works.


'''
AUTO_USERS = {
    'SUPER': {
        'kalle': {
            'first_name': 'Kalle',
            'last_name': 'Westerling',
            'password': 'admin',
            'groups': ['Team'],
        },
        'lisa': {
            'first_name': 'Lisa',
            'last_name': 'Rhody',
            'password': 'admin',
            'groups': ['Team'],
        },
        'steve': {
            'first_name': 'Steve',
            'last_name': 'Zweibel',
            'password': 'admin',
            'groups': ['Team'],
        }
    },

    'STAFF': {
        'admin': {
            'first_name': 'Administrator',
            'last_name': 'General',
            'password': 'admin',
            'groups': ['Team'],
        },
        'param': {
            'first_name': 'Param',
            'last_name': 'Ajmera',
            'password': 'admin',
            'groups': ['Team'],
        },
        'di': {
            'first_name': 'Di',
            'last_name': 'Yoong',
            'password': 'admin',
            'groups': ['Team'],
        },
        'filipa': {
            'first_name': 'Filipa',
            'last_name': 'Calado',
            'password': 'admin',
            'groups': ['Team'],
        },
        'rafa': {
            'first_name': 'Rafa',
            'last_name': 'Davis Portela',
            'password': 'admin',
            'groups': ['Team'],
        },
        'stefano': {
            'first_name': 'Stefano',
            'last_name': 'Morello',
            'password': 'admin',
            'groups': ['Team'],
        },
        'kristen': {
            'first_name': 'Kristen',
            'last_name': 'Hackett',
            'password': 'admin',
            'groups': ['Team'],
        }
    },

    'USER': {
        'test': {
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'test',
            'groups': ['Learner'],
        }
    }
}
'''


# MAKE NO CHANGES BELOW


'''
DJANGO_PATHS['DB'] = Path(DJANGO_PATHS['DB'])

for path in DJANGO_PATHS:
    DJANGO_PATHS[path] = Path(__file__).absolute().parent.parent / DJANGO_PATHS[path]
'''  # TODO: Remove after making sure the app works

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


try:
    TERMINAL_WIDTH = os.popen('stty size', 'r').read().split()[1]
    TERMINAL_WIDTH = int(TERMINAL_WIDTH)
except:
    TERMINAL_WIDTH = 70

if TERMINAL_WIDTH > MAX_TERMINAL_WIDTH:
    TERMINAL_WIDTH = MAX_TERMINAL_WIDTH


saved_prefix = '----> '

AUTO_USERS = dict()
try:
    with open(USER_SETUP, 'r') as f:
        AUTO_USERS = yaml.safe_load(f)
except FileNotFoundError:
    # TODO: Figure out import of log and change `print` to `log.error` here
    print(f'Cannot open {USER_SETUP} to read the automatic user information. Make sure your `dhri_settings.py` file contains the correct filename.')
    print('This means that the script will skip the user setup. Run `manage.py createsuperuser` to be able to access the backend.')
    # exit()
except yaml.parser.ParserError as e:
    # TODO: Figure out import of log and change `print` to `log.error` here
    print(f'Cannot parse file {USER_SETUP}: {e}')
    print('This means that the script will skip the user setup. Run `manage.py createsuperuser` to be able to access the backend.')
    # exit()
except yaml.scanner.ScannerError as e:
    # TODO: Figure out import of log and change `print` to `log.error` here
    print(f'Cannot parse file {USER_SETUP}: {e}')
    print('This means that the script will skip the user setup. Run `manage.py createsuperuser` to be able to access the backend.')
    # exit()

REQUIRED_IN_USERS = ['first_name', 'last_name', 'username', 'password']
# AUTO_USERS testing data
for cat in AUTO_USERS:
    for u in AUTO_USERS[cat]:
        for section in REQUIRED_IN_USERS:
            if not u.get(section):
                # TODO: Figure out import of log and change `print` to `log.error` here
                print(
                    f'User setup file does not contain section `{section}` (in user with username `{u.get("username")}`). Make sure all the users in the `{USER_SETUP}` file contains all the required sections: `{"`, `".join(REQUIRED_IN_USERS)}`.')
                exit()

for _, dir in IMAGE_CACHE.items():
    IMAGE_CACHE[_] = Path(dir)
    if not IMAGE_CACHE[_].exists():
        IMAGE_CACHE[_].mkdir(parents=True)
