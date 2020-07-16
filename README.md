# Digital Humanities Research Institute's curriculum website (Django)

This is the alpha 3 version of the DHRI's curriculum website (created as a django app).

Belongs to: [Sprint 3](https://www.github.com/DHRI-Curriculum/django-app/milestone/3)  
Deadline: July 23

---

## Contents

1. [Installing](#1-installing)
2. [Populate Database](#2-populate-database)
3. [Run Server](#3-run-server)

---

## 1. Installing

### Step 1. Clone the repository

```sh
$ git clone https://github.com/DHRI-Curriculum/django-app
Cloning into 'django-app'...
...
Resolving deltas: 100% (1843/1843), done.
```

Then navigate into the repository (`cd django-app`).

### Step 2. Create virtual enviroment

Next, create a virtual environment for Django to run in:

```sh
$ python -m venv env
```

Then activate the environment:

```sh
$ source env/bin/activate
```

### Step 3: Install requirements

The script contains a `requirements.txt` file in the root of the repository, which makes it easy for you to run a command to run all the required dependencies:

```sh
$ pip install -r requirements.txt
Collecting django==3.0.7 (from -r requirements.txt (line 1))
  ...
```

That should show you the progress of the installation of all the python dependencies for the project.

## 2. Populate Database

The Django app comes with built-in support to download all the data from the DHRI Curriculum, in a number of different ways. The most straight-forward way is what follows.

### Step 1. Set up database structure

First, set up the database by running two commands from Django's built-in management script:

```sh
$ python manage.py makemigrations
```

```sh
$ python manage.py migrate
```

### Step 2. Populate with live data

Next, run the custom DHRI command from inside Django's own management script:

```sh
$ python manage.py downloaddata --wipe --all
```

- The `--wipe` parameter resets the database (so it is not necessary if you have just cloned this repository but it's good to keep there to run some housekeeping tasks in other cases).

- The `--all` parameter will download data from _all_ the standard repositories. If you want to see the full list, just run `python manage.py showsettings --repo`. Should you want to make edits, see ["Changing settings"](#changing-settings) below.

## 3. Run Server

You are now all done. You can run the server by running this command:

```
python manage.py runserver
```

_It will automatically create a development server for you, and you should be able to now navigate to http://localhost:8000 (or its alias http://127.0.0.1:8000)_ in a browser on your computer._

### Optional: Enable Access on Local Network (Advanced)

If you want to make your development server accessible through your local network, instead of the command in the Run Server section above, run the following command:

```
python manage.py localserver
```

Note that `localserver` is a custom-made script for the `backend` app here, and _not_ a native Django command.

#### Optional: Adjust Settings

The script above might give you a warning that notifies you that `'*'` has been added to `ALLOWED_HOSTS`. You can rectify that by following these two steps:

- Edit the file `django-app/app/app/settings.py`

- Find the line that reads:

   ```python
   ALLOWED_HOSTS = []
   ```

   ...and change it to:

   ```python
   ALLOWED_HOSTS = ['*']
   ```

---

## Setting up a new workshop

### Step 1: Create the workshop's repository

Inside [DHRI-Curriculum](https://github.com/DHRI-Curriculum/), add whichever repository you need.

If you want to, you can create a new branch inside the repository, specific for the Django data. Make note of the branch where you are building the workshop as you will need it in a future step.

### Step 2: Ensure all files are present

Make sure that all the necessary files are present:

- `frontmatter.md`
- `lessons.md`
- `theory-to-practice.md`
- `assessment.md`

Without those files in the repo (and branch) that you want to use, you will not be able to work with the repository. Also, each of those files have required sections that need to be present inside them. Here is a template for each file:

#### `frontmatter.md`

```md
# Frontmatter

## Abstract

Abstract

## Learning Objectives

- Learning objective 1
- Learning objective 2
- Learning objective 3

## Estimated time

10 hours.

## Prerequisites

- Title of required previous workshop

## Contexts

### Pre-reading suggestions

- Book about R with [link](http://www.google.com)

### Projects that use these skills

- A project with [link](http://www.google.com)

### Ethical Considerations

- Ethical consideration 1
- Ethical consideration 2
- Ethical consideration 3

## Resources (optional)

- Links to required installations
- Shortcut sheets

## Acknowledgements

- Role: [Firstname Lastname](<personal website>)
- Role: [Firstname Lastname](<personal website>)
- Role: [Firstname Lastname](<personal website>)
```

#### `lessons.md`

```md
# Lesson 1

Lesson text

## Challenge

Challenge text

## Solution

Solution text

# Lesson 2

Lesson text

## Challenge

Challenge text

## Solution

Solution text
```

#### `theory-to-practice.md`

```md
# Theory to Practice

## Suggested Further Readings

- Use bullet points for each of the sources (in markdown, you use - on a new line to create a bullet point).
- If the reading has a DOI number, make sure to add it. If it does, you do not need to add any additional bibliographic information.

## Other Tutorials

- Use bullet points for each of the sources (in markdown, you use - on a new line to create a bullet point).
- Programming Historian

## Projects or Challenges to Try

- Further exploration, possible little projects to try — can also use [links](<link>)
- Exercises from other open source tutorials

## Discussion Questions

- Discussion question 1
- Discussion question 2
- Discussion question 3
```

#### `assessment.md`

```md
# Assessment

## Quantitative Self-Assessment

Add each question as a regular paragraph.

- Each question should have multiple choice answers, added as bullet points under the paragraph.
- Make sure that the questions enable the learner to evaluate their understanding of specific concepts from the workshop.

## Qualitative Self-Assessment

Add each question as a regular paragraph. These qualitative questions (of course) do not need to have answers but should enable the learner to think about what they learned and how it can be used.

- If you think of readings/tutorials/projects/challenges from the "Theory to Practice" section to direct them to, and add a note of that as a bullet point under relevant questions.
```

### Step 3: Download data to Django

```sh
$ python manage.py downloaddata --repos <repo-name>
```

It will ask for the branch name, and load everything from the repository.

---

## Changing Settings

All the settings for the DHRI script lives inside `/backend/dhri_settings.py`. This is a list of the out-of-the-box settings (as of alpha-3) and an explanatio of what they do.

### Cache variables

#### CACHE_DIRS

A dictionary that determines the path of the different caches for the DHRI Curriculum helper, with three categories in the key positions (`ROOT`, `WEB`, `ZOTERO`), and their directories in the value position.

```py
CACHE_DIRS = {
    'ROOT': '.loader-cache/',
    'WEB': '.loader-cache/web/',
    'ZOTERO': '.loader-cache/zotero/'
}
```

#### TEST_AGES

A dictionary that defines the expiry age for the cache categories defined as in the `CACHE_DIRS`, where (as of alpha-3), `ROOT` and `WEB` are defined with minutes in the value position, and `ZOTERO` with days in the value position:

```py
TEST_AGES = {
    'ROOT': 20160, # 20,160 minutes = 14 days
    'WEB': 20160, # 20,160 minutes = 14 days
    'ZOTERO': 14, # days
}
```

#### FORCE_DOWNLOAD

A boolean that, if set to `True`, will ensure the cache is overridden every time (effectively disregarding `TEST_AGES` above).

```py
FORCE_DOWNLOAD = False
```

### Development features

#### DEBUG

~~A boolean that, if set to `True`, will ensure the database is erased and reset for each run.~~ **This setting is not in use as of alpha-3.** #TODO: Ensure

```py
DEBUG = True
```

#### VERBOSE

A boolean that, if set to `True`, will ensure that any custom-made scripts for DHRI outputs all of the information about the process possible.

```py
VERBOSE = False
```

#### AUTO_RESET

~~A boolean that, if set to `True`, will ensure all the DHRI curriculum database elements reset automatically before script runs (not recommended in production).~~ **This setting is not in use as of alpha-3.** #TODO: Ensure

```py
AUTO_RESET = True
```

### Standard settings

#### AUTO_REPOS

A list of tuples containing the repository name in the first position and the branch in the second position

```py
[
    ('project-lab', 'v2.0rhody-edits'),
    ('data-and-ethics', 'v2.0-di-edits'),
    ('text-analysis', 'v2.0-rafa-edits'),
    ('command-line', 'v2.0-smorello-edits'),
    ('python', 'v2.0-filipa-edits'),
    ('html-css', 'v2.0-param-edits'),
    ('git', 'v2.0-kristen-edits'),
]
```

#### AUTO_PAGES

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

#### AUTO_GROUPS

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

#### AUTO_USERS

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

#### FIXTURE_PATH

~~This is where the final fixtures JSON file will be saved~~ **This setting is not in use as of alpha-3.** #TODO: Ensure

```py
FIXTURE_PATH = 'app/fixtures.json'
```

#### BACKEND_AUTO, REPO_AUTO, BRANCH_AUTO

**These settings are not in use as of alpha-3.** #TODO: Ensure

```py
BACKEND_AUTO = 'Github'
REPO_AUTO = ''
BRANCH_AUTO = 'v2.0'
```

#### MAX_TERMINAL_WIDTH, AUTO_TERMINAL_WIDTH

These two set the automatic and maximum size for terminal output.

```py
MAX_TERMINAL_WIDTH = 140
AUTO_TERMINAL_WIDTH = 70
```

#### DJANGO_PATHS

**These settings are not in use as of alpha-3.** #TODO: Ensure

```py
DJANGO_PATHS = {
      'DJANGO': 'app/',
      'DB': 'app/db.sqlite3',
      'MANAGE': 'app/manage.py',
   }
```

#### ZOTERO_API_KEY

**These settings are not yet in use for alpha-3.** #TODO: Ensure

```py
try:
    with open('./zotero-api-key.txt', 'r') as f:
        ZOTERO_API_KEY = f.read()
except:
    ZOTERO_API_KEY = None
```

#### REPLACEMENTS

A dictionary that contains automatic replacements for repository names, where keys are replaced by the values.

```py
REPLACEMENTS = {
    '-': ' ',
    'Html Css': 'HTML/CSS',
}
```

#### NORMALIZING_SECTIONS

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

#### REQUIRED_SECTIONS

~~A dictionary of the required sections for each category in the DHRI Curriculum files~~ **This setting is not in use as of alpha-3.** #TODO: Ensure

#### LESSON_TRANSPOSITIONS

A replacement dictionary, where any occurrences of key position in the lesson text for each lesson in each processed DHRI Curriculum, will be replaced by the value position.

```py
LESSON_TRANSPOSITIONS = {
    '<!-- context: terminal -->': '<img src="terminal.png" />'
}
```

#### STATIC_IMAGES

A replacement dictionary, where image `src` attributes' directories will be replaced for each category (key position) with the value position.

```py
STATIC_IMAGES = {
    'LESSONS': Path('./app/workshop/static/images/lessons/')
}
```