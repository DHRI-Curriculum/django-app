from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri_settings import AUTO_REPOS, saved_prefix, AUTO_PAGES

import os
from backend.dhri.log import Logger, get_or_default, log_created
from backend.models import *

from backend.dhri.loader import Loader
from backend.dhri.exceptions import MissingRequiredSection
from backend.dhri.text import auto_replace, get_number
from backend.dhri.markdown import extract_links
from .wipe import wipe

log = Logger(name='downloaddata')



class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Create fixtures from repositories'

    def add_arguments(self, parser):
        parser.add_argument('--wipe', action='store_true')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--repos', nargs='+', type=str)
        group.add_argument('--all', action='store_true')

    def handle(self, *args, **options):
        if options.get('wipe', False):
            wipe()

        if options.get('all', False):
            log.log("Automatic import activated.")
            repos = AUTO_REPOS
        else:
            repos = options.get('repos')

        for repo in repos:
            branch = None
            if isinstance(repo, tuple):
                repo, branch = repo

            if not branch:
                for REPO in AUTO_REPOS:
                    if repo == REPO[0]:
                        branch = REPO[1]

            if not branch:
                while not branch:
                    branch = get_or_default(f'What is the branch name you want to import?', '')

            repo = f'https://github.com/DHRI-Curriculum/{repo}'

            try:
                l = Loader(repo, branch)
            except MissingRequiredSection:
                log.error(f"One or more required section(s) could not be found in {l.repo_name}.", kill=False)

            ###### Test for data consistency
            if sum([l.has_frontmatter, l.has_praxis, l.has_assessment]) <= 2:
                log.error(f"The repository {l.repo_name} does not have enough required files present. The import of the entire repository will be skipped.", kill=None)
                continue

            if options.get('all', False):
                repo_name = l.meta['repo_name']
            else:
                repo_name = get_or_default('Repository', l.meta['repo_name'])

            repo_name = get_or_default('Workshop name', auto_replace(repo_name.title()))
            log.name = l.repo_name
            log.original_name = log.name

            workshop, created = Workshop.objects.get_or_create(
                name = repo_name,
                defaults = {
                    'parent_backend': l.parent_backend,
                    'parent_repo': l.parent_repo,
                    'parent_branch': l.parent_branch
                }
            )
            if created:
                log.log(saved_prefix + f'Workshop {workshop.name} added (ID {workshop.id}).')
            else:
                log.warning(f'Workshop {workshop.name} already exists (ID {workshop.id}).')

            log.name = log.original_name + "-lessons"
            if l.has_lessons:
                for lesson_data in l.as_html.lessons:
                    try:
                        order += 1
                    except:
                        order = 1

                    lesson, created = Lesson.objects.get_or_create(
                        workshop = workshop,
                        title = lesson_data['title'],
                        defaults = {
                            'text': lesson_data['text'],
                            'order': order
                        }
                    )
                    log_created(created, 'Lesson', lesson.title, lesson.id, log)

                    if lesson_data['challenge']:
                        challenge, created = Challenge.objects.get_or_create(
                            lesson = lesson,
                            text = lesson_data['challenge']
                        )
                        log_created(created, 'Challenge', challenge.text[:20] + '...', challenge.id, log)

                        if lesson_data['solution']:
                            obj, created = Solution.objects.get_or_create(
                                challenge = challenge,
                                text = lesson_data['solution']
                            )
                            log_created(created, 'Solution', obj.text[:20] + '...', obj.id, log)

                        processed_solution = True

                    if lesson_data['solution']:
                        try:
                            processed_solution
                        except:
                            log.error(f'Lesson `{lesson.title}` has a solution but no challenge. Will continue but not insert the solution.', kill=False)

                del order

            # TODO: move...
            def process_links(input, obj):
                links = extract_links(input)
                if links:
                    title, url = links[0]
                else:
                    return(None, None)
                if len(links) > 1:
                    log.warning(f'One project seems to contain more than one URL, but only one ({url}) is captured: {links}')
                if title == None or title == '':
                    from backend.dhri.webcache import WebCache
                    title = WebCache(url).title
                    title = get_or_default(f'Set a title for the {obj} at {url}: ', title)
                return(title, url)

            log.name = log.original_name + "-frontmatter"
            for model in l.frontmatter_models:

                if model == Frontmatter:
                    frontmatter, created = model.objects.get_or_create(
                        workshop = workshop,
                        defaults = {
                            'abstract': l.abstract,
                            'estimated_time': get_number(l.frontmatter['estimated_time'])
                        }
                    )
                    log_created(created, 'Frontmatter for', frontmatter.workshop, frontmatter.id, log)

                elif model == EthicalConsideration:
                    for label in l.ethical_considerations:
                        obj, created = model.objects.get_or_create(frontmatter = frontmatter, label = label)
                        log_created(created, 'Ethical Consideration', obj.label[:20] + '...', obj.id, log)

                elif model == LearningObjective:
                    for label in l.learning_objectives:
                        obj, created = model.objects.get_or_create(frontmatter = frontmatter, label = label)
                        log_created(created, 'Learning Objective', obj.label[:20] + '...', obj.id, log)

                elif model == Project:
                    for annotation in l.projects:
                        title, url = process_links(annotation, 'project')
                        obj, created = model.objects.get_or_create(annotation = annotation, title = title, url = url)
                        log_created(created, 'Project', obj.title, obj.id, log)
                        frontmatter.projects.add(obj)

                elif model == Reading:
                    for annotation in l.readings:
                        title, url = process_links(annotation, 'reading')
                        obj, created = model.objects.get_or_create(annotation = annotation, title = title, url = url)
                        log_created(created, 'Reading', obj.title, obj.id, log)
                        frontmatter.readings.add(obj)

                elif model == Contributor:
                    for contributor in l.contributors:
                        obj, created = model.objects.get_or_create(
                            first_name = contributor.get('first_name'),
                            last_name = contributor.get('last_name'),
                            role = contributor.get('role'),
                            url = contributor.get('url'),
                        )
                        log_created(created, 'Contributor', obj.full_name, obj.id, log)

                else:
                    log.error(f'Have no way of processing {model} for app `frontmatter`. The `downloaddata` script must be adjusted accordingly.', kill=False)

            log.name = log.original_name + "-praxis"
            for model in l.praxis_models:

                if model == Praxis:
                    praxis, created = model.objects.get_or_create(
                        workshop = workshop,
                        defaults = {
                            'discussion_questions': l.discussion_questions,
                            'next_steps': l.next_steps
                        }
                    )
                    log_created(created, 'Theory-to-practice for', praxis.workshop, praxis.id, log)

                elif model == Tutorial:
                    for annotation in l.tutorials:
                        label, url = process_links(annotation, 'tutorial')
                        obj, created = model.objects.get_or_create(annotation = annotation, label = label, url = url)
                        log_created(created, 'Tutorial', obj.label, obj.id, log)
                        praxis.tutorials.add(obj)

                elif model == Reading:
                    for annotation in l.further_readings:
                        title, url = process_links(annotation, 'reading')
                        obj, created = model.objects.get_or_create(annotation = annotation, title = title, url = url)
                        log_created(created, 'Reading', obj.title, obj.id, log)
                        praxis.further_readings.add(obj)

                else:
                    log.error(f'Have no way of processing {model} for app `praxis`. The `downloaddata` script must be adjusted accordingly.', kill=False)


        # TODO: move into loadpages
        log.name = log.original_name + "-pages"
        for p in AUTO_PAGES:
            page, created = Page.objects.get_or_create(
                name = p.get('name', None),
                text = p.get('text', None),
                defaults = {
                    'template': p.get('template', None),
                    'slug': p.get('slug', None)
                }
            )

        from .loadgroups import create_groups
        create_groups()

        from .loadusers import create_users
        create_users()

        # TODO: Dump data?