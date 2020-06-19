## Using populate to create fixture for Django

from dhri.utils.markdown import get_bulletpoints, is_exclusively_bullets, get_list
from dhri.utils.loader import Loader
from dhri.utils.text import get_urls, get_number, get_markdown_hrefs

from dhri.backend import *
from dhri.models import *
from dhri.meta import reset_all, get_or_default

from django.utils.text import slugify

import json

all_ = [
        (('project-lab'), ('v2.0rhody-edits')),
        (('command-line'), ('v2.0-smorello-edits')),
    ]

pks = {
    # workshop.models
    'workshop': 0,

    # frontmatter.models
    'frontmatter': 0,
    'learning_objective': 0,
    'project': 0,
    'resource': 0,
    'reading': 0,
    'contributor': 0,

    # praxis.models...

    # assessment.models...
}


class Data():

    def __init__(workshop_pk):
        


for werkshop in all_:
    repo, branch = werkshop
    repo = f"https://github.com/DHRI-Curriculum/{repo}"

    l = Loader(repo, branch)


    data = []

    
    pks['workshop'] += 1

    data.append({
            "model": "workshop.Workshop",
            "pk": pks['workshop'],
            "fields": {
                "name": l.name,
                "slug": slugify(l.name),
                "parent_backend": "GitHub",
                "parent_repo": l.repo_name,
                "parent_branch": branch,
            }
        })


    data.append({
            "model": "workshop.Frontmatter",
            "pk": pks['frontmatter'],
            "fields": {
                "name": l.name,
                "slug": slugify(l.name),
                "parent_backend": "GitHub",
                "parent_repo": l.repo_name,
                "parent_branch": branch,
            }
        })

    
    print(data)