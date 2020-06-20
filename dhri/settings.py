

# Which repositories and branches should we do automatically?
AUTO_PROCESS = [
        ('project-lab', 'v2.0rhody-edits'),
        ('command-line', 'v2.0-smorello-edits'),
        ('python', 'v2.0-filipa-edits'),
        ('text-analysis', 'v2.0-rafa-edits'),
        ('html-css', 'v2.0-param-edits'),
        ('git', 'v2.0'),
        ('data-and-ethics', 'v2.0'),
    ]

# if VERBOSE is set to True, every output message will display the source module (good for troubleshooting)
VERBOSE = True

FIXTURE_PATH = 'app/fixtures.json' # This is where the final fixtures JSON file will be saved

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

REQUIRED_SECTIONS = {
    'frontmatter': set(NORMALIZING_SECTIONS['frontmatter'].keys()),
    'theory-to-practice': set(NORMALIZING_SECTIONS['theory-to-practice'].keys()),
    'assessment': set(NORMALIZING_SECTIONS['assessment'].keys())
}



DOWNLOAD_CACHE_DIR = './__loader-cache__'
TEST_AGE = 60 # minutes


MAX_TERMINAL_WIDTH = 140
AUTO_TERMINAL_WIDTH = 70


