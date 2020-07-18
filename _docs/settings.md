# Changing Settings

All the settings for the DHRI script lives inside `/backend/dhri_settings.py`. This is a list of the out-of-the-box settings (as of alpha-3) and an explanatio of what they do.

## Cache variables

### CACHE_DIRS

A dictionary that determines the path of the different caches for the DHRI Curriculum helper, with three categories in the key positions (`ROOT`, `WEB`, `ZOTERO`), and their directories in the value position.

```py
CACHE_DIRS = {
    'ROOT': '.loader-cache/',
    'WEB': '.loader-cache/web/',
    'ZOTERO': '.loader-cache/zotero/'
}
```

### TEST_AGES

A dictionary that defines the expiry age for the cache categories defined as in the `CACHE_DIRS`, where (as of alpha-3), `ROOT` and `WEB` are defined with minutes in the value position, and `ZOTERO` with days in the value position:

```py
TEST_AGES = {
    'ROOT': 20160, # 20,160 minutes = 14 days
    'WEB': 20160, # 20,160 minutes = 14 days
    'ZOTERO': 14, # days
}
```

### FORCE_DOWNLOAD

A boolean that, if set to `True`, will ensure the cache is overridden every time (effectively disregarding `TEST_AGES` above).

```py
FORCE_DOWNLOAD = False
```

## Development features

### DEBUG

~~A boolean that, if set to `True`, will ensure the database is erased and reset for each run.~~ **This setting is not in use as of alpha-3.** #TODO: Ensure

```py
DEBUG = True
```

### VERBOSE

A boolean that, if set to `True`, will ensure that any custom-made scripts for DHRI outputs all of the information about the process possible.

```py
VERBOSE = False
```

### AUTO_RESET

~~A boolean that, if set to `True`, will ensure all the DHRI curriculum database elements reset automatically before script runs (not recommended in production).~~ **This setting is not in use as of alpha-3.** #TODO: Ensure

```py
AUTO_RESET = True
```

## Standard settings

### AUTO_REPOS

A list of tuples containing the repository name in the first position and the branch in the second position

```py
[
    ('project-lab', 'v2.0rhody-edits'),
    ('data-literacies', 'v2.0-di-edits'),
    ('text-analysis', 'v2.0-rafa-edits'),
    ('command-line', 'v2.0-smorello-edits'),
    ('python', 'v2.0-filipa-edits'),
    ('html-css', 'v2.0-param-edits'),
    ('git', 'v2.0-kristen-edits'),
]
```

### AUTO_PAGES

A list of dictionaries that define the details of pages to automatically create using `python manage.py loadpages` #TODO: Set this up. The `Workshops` and `Library` pages are necessary for the website's basic functionality.

```py
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
```

### AUTO_GROUPS

A dictionary of groups in the key position, with a dictionary as value. The second level dictionary consists of a Django database model as the key, and a list of allowed actions as the value.

Currently (as of alpha-3) there is only one group added (`Team`), with full administrative access to all the models (`['add', 'change', 'delete', 'view']`). The dictionary also contains the name of another group (`Learner`) which is the automatically assigned group for anyone who signs up as a "user" (or "learner") on the site. The `Learner` group does not have any privileges.

The dictionary controls the command:

```sh
$ python manage.py loadgroups
```

It is also invocated in the `downloaddata` command that may be passed to `manage.py`.

```py
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
```

### AUTO_USERS

A dictionary of user categories (`SUPER`, `STAFF`, `USER`) in the key position, and a second-level dictionary in the value position. The second-level dictionary has usernames in the key position, and a third-level dictionary defining the details of the user in the value position.

The dictionary controls the command:

```sh
$ python manage.py loadusers
```

It is also invocated in the `downloaddata` command that may be passed to `manage.py`.

```py
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
```

### FIXTURE_PATH

~~This is where the final fixtures JSON file will be saved~~ **This setting is not in use as of alpha-3.** #TODO: Ensure

```py
FIXTURE_PATH = 'app/fixtures.json'
```

### BACKEND_AUTO, REPO_AUTO, BRANCH_AUTO

**These settings are not in use as of alpha-3.** #TODO: Ensure

```py
BACKEND_AUTO = 'Github'
REPO_AUTO = ''
BRANCH_AUTO = 'v2.0'
```

### MAX_TERMINAL_WIDTH, AUTO_TERMINAL_WIDTH

These two set the automatic and maximum size for terminal output.

```py
MAX_TERMINAL_WIDTH = 140
AUTO_TERMINAL_WIDTH = 70
```

### DJANGO_PATHS

**These settings are not in use as of alpha-3.** #TODO: Ensure

```py
DJANGO_PATHS = {
      'DJANGO': 'app/',
      'DB': 'app/db.sqlite3',
      'MANAGE': 'app/manage.py',
   }
```

### ZOTERO_API_KEY

**These settings are not yet in use for alpha-3.** #TODO: Ensure

```py
try:
    with open('./zotero-api-key.txt', 'r') as f:
        ZOTERO_API_KEY = f.read()
except:
    ZOTERO_API_KEY = None
```

### REPLACEMENTS

A dictionary that contains automatic replacements for repository names, where keys are replaced by the values.

```py
REPLACEMENTS = {
    '-': ' ',
    'Html Css': 'HTML/CSS',
}
```

### NORMALIZING_SECTIONS

A dictionary that specifies how sections in the DHRI Curriculum files will be interpreted. In the key position is the file prefix (`frontmatter`, `theory-to-practice`, `assessment`) and in the value position is a second-level dictionary with the normalized value in the key position (_these are programmatic and should not be changed_). In the second-level dictionary's value position is a list of possible variations/spellings that will be converted into the normalized values.

```py
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
```

### REQUIRED_SECTIONS

~~A dictionary of the required sections for each category in the DHRI Curriculum files~~ **This setting is not in use as of alpha-3.** #TODO: Ensure

### LESSON_TRANSPOSITIONS

A replacement dictionary, where any occurrences of key position in the lesson text for each lesson in each processed DHRI Curriculum, will be replaced by the value position.

```py
LESSON_TRANSPOSITIONS = {
    '<!-- context: terminal -->': '<img src="terminal.png" />'
}
```

### STATIC_IMAGES

A replacement dictionary, where image `src` attributes' directories will be replaced for each category (key position) with the value position.

```py
STATIC_IMAGES = {
    'LESSONS': Path('./app/workshop/static/images/lessons/')
}
```