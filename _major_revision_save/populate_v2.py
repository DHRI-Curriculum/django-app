# populate_v2

from dhri.settings import AUTO_PROCESS, LESSON_TRANSPOSITIONS
from dhri.utils.webcache import WebCache
from dhri.utils.text import auto_replace
from dhri.django import django
from django.utils.text import slugify

# Setup logging
from dhri.interaction import Logger, get_or_default
log = Logger(name="main")

done, iteration, collect_workshop_slugs = 'n', 0, list()

counters = {
    'workshop': 0,
    'lesson': 0
}
data = {
    'workshop': [],
    'lesson': [],
}

if __name__ == '__main__':
    while done == 'n':
        try:
            repo, branch = AUTO_PROCESS.pop(0)
            log.log(f'In AUTO_PROCESS mode: Current iteration {iteration}. Processing {repo}/{branch}, Remaining: {len(AUTO_PROCESS)}. Finished workshops: {collect_workshop_slugs}')
        except IndexError:
            repo = get_or_default(f'What is the repo name (assuming DHRI-Curriculum as username) or whole GitHub link you want to import?', repo)
            if repo == '':
                log.error('No repository name, exiting...', kill=None)
                done = 'y'
                continue

            branch = get_or_default(f'What is the branch name you want to import?', branch)
            if branch == '':
                log.error('No branch name, exiting...', kill=None)
                done = 'y'
                continue

        if not repo.startswith('https://github.com/'): # FIXME: If we decide to move to a different backend
            repo = f'https://github.com/DHRI-Curriculum/{repo}'

        ###### Load in data from GitHub (handled by dhri.utils.loader.Loader)

        from dhri.utils.loader import Loader
        from dhri.utils.exceptions import MissingRequiredSection

        try:
            l = Loader(repo, branch)
        except MissingRequiredSection:
            log.error(f"One or more required section(s) could not be found in {l.repo_name}.", kill=False)

        if AUTO_PROCESS:
            repo_name = l.repo_name
        else:
            repo_name = get_or_default('Repository', l.repo_name)

        repo_name = get_or_default('Workshop name', auto_replace(repo_name.title()))
        log.name = l.repo_name
        log.original_name = log.name

        ###### WORKSHOP MODEL ####################################

        log.name = log.original_name + "-workshop"
        counters['workshop'] += 1
        data['workshop'].append({
            'model': 'workshop.workshop',
            'pk': counters['workshop'],
            'fields': {
                'name': repo_name,
                'slug': slugify(repo_name),
                'parent_backend': l.parent_backend,
                'parent_repo': l.parent_repo,
                'parent_branch': l.parent_branch,
            }
        })

        if l.has_lessons:
            order = 1

            from pathlib import Path
            from dhri.utils.parse_lesson import download_image
            from bs4 import BeautifulSoup
            from bs4 import Comment

            STATIC_IMAGES = Path('./app/workshop/static/images/lessons/')
            REPO_CLEAR = "".join(repo.split("https://github.com/DHRI-Curriculum/")[1:])

            for lesson_data in l.as_html.lessons:

                counters['lesson'] += 1

                data['lesson'].append({
                    'model': 'lesson.lesson',
                    'pk': counters['lesson'],
                    'fields': {
                        'workshop': counters['workshop'],
                        'title': lesson_data['title'],
                        'text': clean_html,
                        'order': counters['lesson']
                    }
                })

                if lesson_data['challenge']:
                    pass # TODO: Fix this here

                if lesson_data['solution']:
                    pass # TODO: Fix this here

        if l.has_frontmatter:

        print(data)
