REQUIRED_SECTIONS = {}

##################################################################

FIXTURE_PATH = 'app/fixtures.json' # This is where the final fixtures JSON file will be saved

# Which repositories and branches should we do automatically?
AUTO_PROCESS = [
        ('command-line', 'v2.0-smorello-edits'),
        ('project-lab', 'v2.0rhody-edits'),
        ('python', 'v2.0-filipa-edits'),
        ('text-analysis', 'v2.0-rafa-edits'),
        ('html-css', 'v2.0-param-edits'),
        ('git', 'v2.0'),
        ('data-and-ethics', 'v2.0'),
    ]

FORCE_DOWNLOAD = True # If set to True, the script will bypass the cache every time (effectively disregarding TEST_AGE below)

AUTO_RESET = True # reset all the DHRI curriculum database elements automatically before script runs (not recommended in production)
DELETE_FILE = True # delete file after script is done

BACKEND_AUTO = 'Github'
REPO_AUTO = ''
BRANCH_AUTO = 'v2.0'


REMOVE_EMPTY_HEADINGS = True    # removing empty headings from sectioning of markdown
BULLETPOINTS_TO_LISTS = True    # remakes sections that ONLY contain bulletpoints into python lists


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

REQUIRED_SECTIONS['frontmatter'] = set(NORMALIZING_SECTIONS['frontmatter'].keys())
REQUIRED_SECTIONS['theory-to-practice'] = set(NORMALIZING_SECTIONS['theory-to-practice'].keys())
REQUIRED_SECTIONS['assessment'] = set(NORMALIZING_SECTIONS['assessment'].keys())



DOWNLOAD_CACHE_DIR = './__loader-cache__'

TEST_AGE = 60 # minutes


MAX_TERMINAL_WIDTH = 140
AUTO_TERMINAL_WIDTH = 70





######## DO NOT EDIT BELOW THIS LINE IF YOU DON'T KNOW WHAT YOU ARE DOING ##############

# Make sure to set up a test of all of the constants

from dhri.logger import Logger
from dhri.utils.exceptions import ConstantError
from itertools import chain
from datetime import timedelta
from pathlib import Path
import os

log = Logger()

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

# Run tests

_check_normalizer()
_test(constant=REMOVE_EMPTY_HEADINGS)
_test(constant=BULLETPOINTS_TO_LISTS)


try:
    TERMINAL_WIDTH = os.popen('stty size', 'r').read().split()[1]
    TERMINAL_WIDTH = int(TERMINAL_WIDTH)
except:
    TERMINAL_WIDTH = 70

if TERMINAL_WIDTH > MAX_TERMINAL_WIDTH: TERMINAL_WIDTH = MAX_TERMINAL_WIDTH
