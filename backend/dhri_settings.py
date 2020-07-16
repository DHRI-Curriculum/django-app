from backend import models
from django.conf import settings
import os

AUTO_REPOS = [
    ('project-lab', 'v2.0rhody-edits'),
    ('data-and-ethics', 'v2.0-di-edits'),
    ('text-analysis', 'v2.0-rafa-edits'),
    ('command-line', 'v2.0-smorello-edits'),
    ('python', 'v2.0-filipa-edits'),
    ('html-css', 'v2.0-param-edits'),
    ('git', 'v2.0-kristen-edits'),
]

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
        models.Page: ['add', 'change', 'delete', 'view'],
        models.Workshop: ['add', 'change', 'delete', 'view'],
    },

    'Learner': {

    }
}

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


##### Standard settings ##############################

# This is where the final fixtures JSON file will be saved
FIXTURE_PATH = 'app/fixtures.json'

BACKEND_AUTO = 'Github'
REPO_AUTO = ''
BRANCH_AUTO = 'v2.0'

# Set the automatic and maximum size for terminal output
MAX_TERMINAL_WIDTH = 140
AUTO_TERMINAL_WIDTH = 70

# Django backend settings
DJANGO_PATHS = {
        'DJANGO': 'app/',
        'DB': 'app/db.sqlite3',
        'MANAGE': 'app/manage.py',
    }

# Zotero API key
try:
    with open('./zotero-api-key.txt', 'r') as f:
        ZOTERO_API_KEY = f.read()
except:
    ZOTERO_API_KEY = None


# Auto replacement in titles
REPLACEMENTS = {
    '-': ' ',
    'Html Css': 'HTML/CSS',
}

##### Cache ##############################

CACHE_DIRS = {
    'ROOT': '.loader-cache/',
    'WEB': '.loader-cache/web/',
    'ZOTERO': '.loader-cache/zotero/'
}

TEST_AGES = {
    'ROOT': 20160, # 20,160 minutes = 14 days
    'WEB': 20160, # 20,160 minutes = 14 days
    'ZOTERO': 14, # days
}

# If set to True, the script will override the cache every time (effectively disregarding TEST_AGES above)
FORCE_DOWNLOAD = False


##### Dev features ##############################

# If set to True, the database will be erased and reset for each run
DEBUG = True

# If VERBOSE is set to True, every output message will display the source module (good for troubleshooting)
VERBOSE = False

# If set to True, resets all the DHRI curriculum database elements automatically before script runs (not recommended in production)
AUTO_RESET = True




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
    'LESSONS': os.path.join(settings.BASE_DIR, 'workshop/static/images/lessons/')
}

AUTO_PAGES = [
    {
        'name': 'Workshops',
        'slug': 'workshops',
        'text': '<p class="lead">This is the workshop page.</p>',
        'template': 'workshop/workshop-list.html',
    },
    {
        'name': 'About',
        'slug': 'about',
        'text': '<p class="lead">This is the about page.</p>',
        'template': 'website/page.html',
    },
    {
        'name': 'Library',
        'slug': 'library',
        'text': '<p class="lead">This is the library page.</p>',
        'template': 'library/all-library-items.html',
    },
]




#### MAKE NO CHANGES BELOW


from itertools import chain
from datetime import timedelta
from pathlib import Path
import os


DJANGO_PATHS['DB'] = Path(DJANGO_PATHS['DB'])

for path in DJANGO_PATHS:
    DJANGO_PATHS[path] = Path(__file__).absolute().parent.parent / DJANGO_PATHS[path]

for cat in STATIC_IMAGES:
    STATIC_IMAGES[cat] = Path(STATIC_IMAGES[cat])

def _test(constant=None, as_type=bool):
    if not isinstance(constant, as_type): log.error(f'{constant}` provided must be a {as_type}.', raise_error=ConstantError)
    return(True)

def _check_normalizer(dictionary=NORMALIZING_SECTIONS):
    for section in NORMALIZING_SECTIONS:
        all_ = [x.lower() for x in list(chain.from_iterable([x for x in NORMALIZING_SECTIONS[section].values()]))]

        if max([all_.count(x) for x in set(all_)]) > 1:
            log.error('NORMALIZING_SECTIONS is confusing: multiple alternative strings for normalizing.', raise_error=ConstantError)

    return(True)


for DIR in CACHE_DIRS:
    CACHE_DIRS[DIR] = Path(CACHE_DIRS[DIR])
    if not CACHE_DIRS[DIR].exists(): CACHE_DIRS[DIR].mkdir()

TEST_AGES['ROOT'] = timedelta(minutes=TEST_AGES['ROOT'])
TEST_AGES['WEB'] = timedelta(minutes=TEST_AGES['WEB'])
TEST_AGES['ZOTERO'] = timedelta(days=TEST_AGES['ZOTERO'])

# Run tests

_check_normalizer()


try:
    TERMINAL_WIDTH = os.popen('stty size', 'r').read().split()[1]
    TERMINAL_WIDTH = int(TERMINAL_WIDTH)
except:
    TERMINAL_WIDTH = 70

if TERMINAL_WIDTH > MAX_TERMINAL_WIDTH: TERMINAL_WIDTH = MAX_TERMINAL_WIDTH


saved_prefix = '----> '