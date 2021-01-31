from library.models import Project, Reading, Tutorial
from workshop.models import Collaboration, Contributor, DiscussionQuestion, EthicalConsideration, LearningObjective, NextStep
from django.core.management import BaseCommand
from django.conf import settings
from django.db.utils import IntegrityError
from backend.dhri.log import Logger, Input
from backend.mixins import convert_html_quotes
from .imports import Workshop, Frontmatter, Profile, Praxis, Lesson, Question, Answer
from ._shared import test_for_required_files, get_yaml, get_name, dhri_slugify

import yaml
import pathlib
import os

log = Logger(name=get_name(__file__))
input = Input(name=get_name(__file__))
WORKSHOPS_DIR = settings.BASE_DIR + '/_preload/_workshops'


def get_all_existing_workshops(specific_names=None):
    if not specific_names:
        return [(x, f'{WORKSHOPS_DIR}/{x}') for x in os.listdir(WORKSHOPS_DIR) if not x.startswith('.')]
    
    _ = list()
    for name in specific_names:
        if name in os.listdir(WORKSHOPS_DIR):
            _.append((name, f'{WORKSHOPS_DIR}/{name}'))
        else:
            log.error(f'The workshop `{name}` failed to ingest as the workshop\'s directory has yet to be created. Try running python manage.py buildworkshop --name {name} before running this command again.')
    return _


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with information about all the existing workshops into the database'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')
        parser.add_argument('--name', nargs='+', type=str)

    def handle(self, *args, **options):

        # Temp here - remove
        # Workshop.objects.all().delete()

        workshops = get_all_existing_workshops()
        
        if options.get('name'):
            workshops = get_all_existing_workshops(options.get('name'))

        for _ in workshops:
            name, path = _
            DATAFILE = f'{path}/{name}.yml'
            
            superdata = get_yaml(DATAFILE)

            # Separate out data
            frontmatterdata = superdata.get('frontmatter')
            praxisdata = superdata.get('praxis')
            lessondata = superdata.get('lessons')
            workshopdata = superdata.get('workshop')

            # 1. ENTER WORKSHOP
            workshop, created = Workshop.objects.get_or_create(
                name = workshopdata.get('name'),
                defaults = {
                    'name': workshopdata.get('name'),
                    'parent_backend': workshopdata.get('parent_backend'),
                    'parent_branch': workshopdata.get('parent_branch'),
                    'parent_repo': workshopdata.get('parent_repo')
                })

            workshop.slug = workshopdata.get('slug')
            workshop.save_slug() # Special method for saving the slug in a format that matches the GitHub repositories.

            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Workshop `{workshopdata.get("name")}` already exists. Update with new content? [y/N]')
                if choice.lower() != 'y':
                    continue

            # 2. ENTER FRONTMATTER
            frontmatter, created = Frontmatter.objects.get_or_create(workshop=workshop)

            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Frontmatter for workshop `{workshop}` already exists. Update with new content? [y/N]')
                if choice.lower() != 'y':
                    continue
            
            Frontmatter.objects.filter(workshop=workshop).update(
                abstract = convert_html_quotes(frontmatterdata.get('abstract')),
                estimated_time = frontmatterdata.get('estimated_time')
            )

            frontmatter.refresh_from_db()

            for label in frontmatterdata.get('ethical_considerations'):
                _, created = EthicalConsideration.objects.get_or_create(frontmatter=frontmatter, label=convert_html_quotes(label)) # convert_html_quotes here to make sure the curly quotes are found

            for label in frontmatterdata.get('learning_objectives'):
                _, created = LearningObjective.objects.get_or_create(frontmatter=frontmatter, label=convert_html_quotes(label)) # convert_html_quotes here to make sure the curly quotes are found

            for projectdata in frontmatterdata.get('projects'):
                project, created = Project.objects.get_or_create(title=projectdata.get('title'), url=projectdata.get('url'), annotation=projectdata.get('annotation'))
                frontmatter.projects.add(project)
                frontmatter.save()

            for readingdata in frontmatterdata.get('readings'):
                reading, created = Reading.objects.get_or_create(title=readingdata.get('title'), url=readingdata.get('url'), annotation=readingdata.get('annotation'))
                frontmatter.readings.add(reading)
                frontmatter.save()

            for prereqdata in frontmatterdata.get('prerequisites'):
                pass # print(prereqdata) # TODO: need database models? or do they exist?
            
            for resourcedata in frontmatterdata.get('resources', []):
                pass # print(resourcedata) # TODO: need database models? or do they exist?

            for contributordata in frontmatterdata.get('contributors'):
                profile = Profile.objects.filter(user__first_name=contributordata.get('first_name'), user__last_name=contributordata.get('last_name'))
                if profile.count() == 1:
                    profile = profile[0]
                else:
                    profile = None
                
                contributor, created = Contributor.objects.get_or_create(first_name=contributordata.get('first_name'), last_name=contributordata.get('last_name'))

                if not created and not options.get('forceupdate'):
                    choice = input.ask(
                        f'Contributor `{contributordata.get("first_name")} {contributordata.get("last_name")}` already exists. Update with new content? [y/N]')
                    if choice.lower() != 'y':
                        continue

                Contributor.objects.filter(first_name=contributordata.get('first_name'), last_name=contributordata.get('last_name')).update(
                    url = contributordata.get('url'), 
                    profile = profile
                )

                contributor.refresh_from_db()

                collaboration, created = Collaboration.objects.get_or_create(frontmatter=frontmatter, contributor=contributor)

                if not created and not options.get('forceupdate'):
                    choice = input.ask(
                        f'Collaboration between {contributor} and {workshop} already exists. Update with new content? [y/N]')
                    if choice.lower() != 'y':
                        continue

                Collaboration.objects.filter(frontmatter=frontmatter, contributor=contributor).update(
                    current = contributordata.get('collaboration').get('current'),
                    role = contributordata.get('collaboration').get('role')
                )

                collaboration.refresh_from_db()
        
            # 3. ENTER PRAXIS
            praxis, created = Praxis.objects.get_or_create(workshop=workshop)

            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Theory to Practice for workshop `{workshop}` already exists. Update with new content? [y/N]')
                if choice.lower() != 'y':
                    continue
            
            Praxis.objects.filter(workshop=workshop).update(
                intro = praxisdata.get('intro'),
            )

            praxis.refresh_from_db()

            for questiondata in praxisdata.get('discussion_questions'):
                discussion_question, created = DiscussionQuestion.objects.get_or_create(praxis=praxis, label=convert_html_quotes(questiondata.get('label')), defaults={'order': questiondata.get('order')}) # convert_html_quotes here to make sure the curly quotes are found

                NextStep.objects.filter(praxis=praxis, label=convert_html_quotes(questiondata.get('label'))).update(
                    order = questiondata.get('order')
                )

                discussion_question.refresh_from_db()

            for stepdata in praxisdata.get('next_steps'):
                nextstep, created = NextStep.objects.get_or_create(praxis=praxis, label=convert_html_quotes(stepdata.get('label')), defaults={'order': stepdata.get('order')}) # convert_html_quotes here to make sure the curly quotes are found

                NextStep.objects.filter(praxis=praxis, label=convert_html_quotes(stepdata.get('label'))).update(
                    order = stepdata.get('order')
                )

                nextstep.refresh_from_db()
                
            for readingdata in praxisdata.get('further_readings'):
                reading, created = Reading.objects.get_or_create(title=readingdata.get('title'), url=readingdata.get('url'), annotation=readingdata.get('annotation'))

                praxis.further_readings.add(reading)
                praxis.save()

            for projectdata in praxisdata.get('further_projects'):
                project, created = Project.objects.get_or_create(title=projectdata.get('title'), url=projectdata.get('url'), annotation=projectdata.get('annotation'))

                praxis.further_projects.add(project)
                praxis.save()

            for tutorialdata in praxisdata.get('tutorials'):
                tutorial, created = Tutorial.objects.get_or_create(label=tutorialdata.get('label'), url=tutorialdata.get('url'), annotation=tutorialdata.get('annotation'))

                praxis.tutorials.add(tutorial)
                praxis.save()

            # TODO: add more_resources
            
        # TODO: Lessons.........