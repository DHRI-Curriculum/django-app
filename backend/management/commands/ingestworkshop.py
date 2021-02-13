from pathlib import Path
from bs4 import BeautifulSoup
from glossary.models import Term
from learner.models import Profile
from lesson.models import Challenge, Evaluation, LessonImage, Solution, Lesson, Question, Answer
from resource.models import Resource
from workshop.models import Collaboration, Contributor, DiscussionQuestion, EthicalConsideration, LearningObjective, NextStep, Workshop, Frontmatter, Praxis
from django.core.management import BaseCommand
from django.core.files import File
from django.conf import settings
from django.db.utils import IntegrityError
from backend.logger import Logger, Input
from backend.settings import STATIC_IMAGES
from ._shared import get_yaml, get_all_existing_workshops, GLOSSARY_FILE
import os
from shutil import copyfile


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with information about all the existing workshops into the database'
    requires_migrations_checks = True
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')
        parser.add_argument('--name', nargs='+', type=str)
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--no_reminder', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
                     force_verbose=options.get('verbose'),
                     force_silent=options.get('silent')
                     )
        input = Input(path=__file__)

        workshops = get_all_existing_workshops()

        if options.get('name'):
            workshops = get_all_existing_workshops(options.get('name'))

        for _ in workshops:
            slug, path = _
            DATAFILE = f'{path}/{slug}.yml'

            d = get_yaml(DATAFILE)

            # Separate out data
            imagedata = d.get('image')
            frontmatterdata = d.get('sections').get('frontmatter')
            praxisdata = d.get('sections').get('theory-to-practice')
            lessondata = d.get('sections').get('lessons')
            
            full_name = d.get('name')
            parent_backend = d.get('parent_backend')
            parent_branch = d.get('parent_branch')
            parent_repo = d.get('parent_repo')

            # 1. ENTER WORKSHOP
            workshop, created = Workshop.objects.update_or_create(
                name=full_name, defaults={
                    'parent_backend': parent_backend,
                    'parent_branch': parent_branch,
                    'parent_repo': parent_repo,
                    'image_alt': imagedata['alt']
                }
            )

            def _get_valid_name(filename):
                return filename.replace('@', '') # TODO: should exist a built-in for django here?
            
            def _get_media_path(valid_filename):
                return settings.MEDIA_ROOT + '/' + Workshop.image.field.upload_to + valid_filename

            def _get_media_url(valid_filename):
                return Workshop.image.field.upload_to + valid_filename

            def _image_exists(valid_filename):
                media_path = _get_media_path(valid_filename)
                return os.path.exists(media_path)

            def _get_default_image():
                return Workshop.image.field.default

            if imagedata:
                source_file = imagedata['url']
                valid_filename = _get_valid_name(slug + '-' + os.path.basename(imagedata['url']))
                if not _image_exists(valid_filename):
                    try:
                        with open(source_file, 'rb') as f:
                            workshop.image = File(f, name=valid_filename)
                            workshop.save()
                    except FileNotFoundError:
                        log.error(f'File `{source_file}` could not be found. Did you run `python manage.py buildworkshop` before you ran this command?')
                workshop.image.name = _get_media_url(valid_filename)
                workshop.save()
            else:
                log.warning(f'Workshop {workshop.name} does not have an image assigned to it. Add filepaths to an existing file in your datafile ({DATAFILE}) if you want to update the specific workshop. Default workshop image (`{os.path.basename(_get_default_image())}`) will be assigned.')
                workshop.image.name = Workshop.image.field.default
                workshop.save()
                
                if not _image_exists(_get_valid_name(os.path.basename(_get_default_image()))):
                    log.warning(f'Default workshop image does not exist. You will want to add it manually to the correct folder: {_get_media_path("")}')

            # Saving the slug in a format that matches the GitHub repositories (special method `save_slug`)
            workshop.slug = slug
            workshop.save_slug()

            # 2. ENTER FRONTMATTER
            frontmatter, created = Frontmatter.objects.update_or_create(
                workshop=workshop, defaults={
                    'abstract': frontmatterdata.get('abstract'),
                    'estimated_time': frontmatterdata.get('estimated_time')
                })

            if frontmatterdata.get('ethical_considerations'):
                for point in frontmatterdata.get('ethical_considerations'):
                    _, created = EthicalConsideration.objects.update_or_create(
                        frontmatter=frontmatter, 
                        label=point.get('annotation')
                    )

            if frontmatterdata.get('learning_objectives'):
                for point in frontmatterdata.get('learning_objectives'):
                    _, created = LearningObjective.objects.update_or_create(
                        frontmatter=frontmatter, 
                        label=point.get('annotation')
                    )

            for cat in ['projects', 'readings']:
                if frontmatterdata.get(cat):
                    category, add_field = None, None
                    if cat == 'projects':
                        category = Resource.PROJECT
                        add_field = frontmatter.projects
                    elif cat == 'readings':
                        category = Resource.READING
                        add_field = frontmatter.readings

                    for point in frontmatterdata.get(cat):
                        if not add_field or not category:
                            log.error('Cannot interpret category `{cat}`. Make sure the script is correct and corresponds with the database structure.')

                        obj, created = Resource.objects.update_or_create(
                            category=category,
                            title=point.get('linked_text'),
                            url=point.get('url'),
                            annotation=point.get('annotation')
                        )
                        if obj not in add_field.all():
                            add_field.add(obj)

            if frontmatterdata.get('contributors'):
                for point in frontmatterdata.get('contributors'):
                    profile = None
                    try:
                        profile = Profile.objects.get(user__first_name=point.get('first_name'), user__last_name=point.get('last_name'))
                    except:
                        for p in Profile.objects.all():
                            if f'{p.user.first_name} {p.user.last_name}' == point.get('full_name'):
                                profile = p
                                log.info(f'In-depth search revealed a profile matching the full name for `{workshop.name}` contributor `{point.get("first_name")} {point.get("last_name")}`. It may or may not be the correct person, so make sure you verify it manually.')

                        if not p:
                            log.info(f'Could not find user profile on the curriculum website for contributor `{point.get("full_name")}` (searching by first name `{point.get("first_name")}` and last name `{point.get("last_name")}`).')
                    
                    contributor, created = Contributor.objects.update_or_create(
                        first_name=point.get('first_name'),
                        last_name=point.get('last_name'),
                        defaults={
                            'url': point.get('link'),
                            'profile': profile
                        }
                    )

                    collaboration, created = Collaboration.objects.update_or_create(
                        frontmatter=frontmatter,
                        contributor=contributor,
                        defaults={
                            'current': point.get('current'),
                            'role': point.get('role')
                        }
                    )


            # 3. ENTER PRAXIS
            praxis, created = Praxis.objects.update_or_create(
                workshop=workshop,
                defaults={
                    'intro': praxisdata.get('intro'),
                }
            )

            for cat in ['discussion_questions', 'next_steps']:
                if praxisdata.get(cat):
                    obj = None
                    if cat == 'discussion_questions':
                        obj = DiscussionQuestion
                    elif cat == 'next_steps':
                        obj = NextStep

                    for order, point in enumerate(praxisdata[cat], start=1): # TODO: Should we pull out order manually here? Not necessary, right?
                        obj.objects.update_or_create(
                            praxis=praxis, 
                            label=point.get('annotation'),
                            defaults={
                                'order': order
                            }
                        )

            for cat in ['further_readings', 'further_projects', 'tutorials']:
                if praxisdata.get(cat):
                    category, add_field = None, None
                    if cat == 'further_readings':
                        category = Resource.READING
                        add_field = praxis.further_readings
                    elif cat == 'further_projects':
                        category = Resource.PROJECT
                        add_field = praxis.further_projects
                    elif cat == 'tutorials':
                        category = Resource.TUTORIAL
                        add_field = praxis.tutorials

                    for point in praxisdata.get(cat):
                        if not add_field or not category:
                            log.error('Cannot interpret category `{cat}`. Make sure the script is correct and corresponds with the database structure.')
                        
                        try:
                            obj, created = Resource.objects.update_or_create(
                                category=category,
                                title=point.get('linked_text'),
                                url=point.get('url'),
                                annotation=point.get('annotation')
                            )
                            if obj not in add_field.all():
                                add_field.add(obj)
                        except IntegrityError:
                            obj = Resource.objects.get(
                                category=category,
                                title=point.get('linked_text'),
                                url=point.get('url'),
                            )
                            obj.annotation = point.get('annotation')
                            if obj not in add_field.all():
                                add_field.add(obj)
                            log.info(f'Another resource with the same URL, title, and category already existed so updated with a new annotation: **{point.get("linked_text")} (old)**\n{point.get("annotation")}\n-------\n**{obj.title} (new)**\n{obj.annotation}')

            # 4. ENTER LESSONS

            for lessoninfo in lessondata:
                lesson, created = Lesson.objects.update_or_create(
                    workshop=workshop,
                    title=lessoninfo.get('header'),
                    defaults={
                        'order': lessoninfo.get('order'),
                        'text': lessoninfo.get('content'),
                    })

                for image in lessoninfo.get('lesson_images'):
                    LessonImage.objects.update_or_create(
                        url=image.get('path'), lesson=lesson, alt=image.get('alt'))

                if not lessoninfo.get('challenge') and lessoninfo.get('solution'):
                    log.error(f'Lesson `{lesson.title}` (in workshop {workshop}) has a solution but no challenge. Correct the files on GitHub and rerun the buildworkshop command and then re-attempt the ingestworkshop command. Alternatively, you can change the datafile content manually.')

                if lessoninfo.get('challenge'):
                    challenge, created = Challenge.objects.update_or_create(
                        lesson=lesson,
                        title=lessoninfo['challenge'].get('header'),
                        text=lessoninfo['challenge'].get('content')
                    )
                
                    if lessoninfo.get('solution'):
                        solution, created = Solution.objects.update_or_create(
                            challenge=challenge,
                            title=lessoninfo['solution'].get('header'),
                            text=lessoninfo['solution'].get('content')
                        )

                if lessoninfo.get('evaluation'):
                    evaluation, created = Evaluation.objects.get_or_create(lesson=lesson)
                    for point in lessoninfo['evaluation'].get('content'):
                        question, created = Question.objects.update_or_create(
                            evaluation=evaluation,
                            label=point.get('question')
                        )
                        for is_correct, answers in point.get('answers').items():
                            is_correct = is_correct == 'correct'
                            for answertext in answers:
                                answer, created = Answer.objects.update_or_create(
                                    question=question,
                                    label=answertext,
                                    defaults={
                                        'is_correct': is_correct
                                    }
                                )

                if lessoninfo.get('keywords'):
                    # lessoninfo['keywords'].get('header') # TODO: not doing anything with keyword header yet
                    for point in lessoninfo['keywords'].get('content'):
                        keyword = point.get('linked_text')
                        terms = Term.objects.filter(term__iexact=keyword)
                        if terms.count() == 1:
                            lesson.terms.add(terms[0])
                        elif terms.count() == 0:
                            log.warning(f'Keyword `{keyword}` (used in lesson `{lesson.title}`, workshop `{workshop}` cannot be found in the existing glossary. Are you sure it is in the glossary and synchronized with the database? Make sure the data file for glossary is available ({GLOSSARY_FILE}) and that the term is defined in the file. Then run python manage.py ingestglossary.')
                        else:
                            log.error(f'Multiple definitions of `{keyword}` exists in the database. Try resetting the glossary and rerun python manage.py ingestglossary before you run the ingestworkshop command again.')

        log.log('Added/updated workshops: ' + ', '.join([x[0] for x in workshops]))
        log.log('Do not forget to run `ingestprerequisites` after running the `ingestworkshop` command (without the --name flag).', color='yellow')

        if log._save(data='ingestworkshop', name='warnings.md', warnings=True) or log._save(data='ingestworkshop', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' +
                    log.LOG_DIR, force=True)
