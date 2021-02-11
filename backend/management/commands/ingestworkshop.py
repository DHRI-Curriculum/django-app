from bs4 import BeautifulSoup
from glossary.models import Term
from learner.models import Profile
from lesson.models import Challenge, Evaluation, LessonImage, Solution, Lesson, Question, Answer
from resource.models import Resource
from workshop.models import Collaboration, Contributor, DiscussionQuestion, EthicalConsideration, LearningObjective, NextStep, Workshop, Frontmatter, Praxis
from django.core.management import BaseCommand
from django.core.files import File
from django.conf import settings
from backend.logger import Logger, Input
from backend.mixins import convert_html_quotes
from ._shared import get_yaml, get_all_existing_workshops, GLOSSARY_FILE
import os


def get_workshop_image_path(image_file, relative_to_upload_field=False):
    workshop = os.path.basename(os.path.dirname(image_file))
    if not relative_to_upload_field:
        return settings.MEDIA_ROOT + '/' + Workshop.image.field.upload_to + workshop + '-' + os.path.basename(image_file)

    return Workshop.image.field.upload_to + workshop + '-' + os.path.basename(image_file)


def workshop_image_exists(image_file):
    return os.path.exists(get_workshop_image_path(image_file))


def get_default_workshop_image():
    return Workshop.image.field.default


def default_workshop_image_exists():
    return os.path.exists(os.path.join(settings.MEDIA_ROOT, get_default_workshop_image()))


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
            name, path = _
            DATAFILE = f'{path}/{name}.yml'

            superdata = get_yaml(DATAFILE)

            print(superdata)
            exit()

            # Separate out data
            frontmatterdata = superdata.get('frontmatter')
            praxisdata = superdata.get('praxis')
            lessondata = superdata.get('lessons')
            workshopdata = superdata.get('workshop')

            # 1. ENTER WORKSHOP
            workshop, created = Workshop.objects.get_or_create(
                name=workshopdata.get('name'))

            workshop.slug = workshopdata.get('slug')
            # Special method for saving the slug in a format that matches the GitHub repositories.
            workshop.save_slug()

            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Workshop `{workshopdata.get("name")}` already exists. Update with new content? [y/N]')
                if choice.lower() != 'y':
                    continue

            Workshop.objects.filter(name=workshopdata.get('name')).update(
                parent_backend=workshopdata.get('parent_backend'),
                parent_branch=workshopdata.get('parent_branch'),
                parent_repo=workshopdata.get('parent_repo'),
            )

            workshop.refresh_from_db()

            if workshopdata.get('image'):
                if workshop_image_exists(workshopdata.get('image')):
                    workshop.image.name = get_workshop_image_path(
                        workshopdata.get('image'), True)
                    workshop.save_slug()
                else:
                    try:
                        with open(workshopdata.get('image'), 'rb') as f:
                            workshop.image = File(
                                f, name=f'{workshopdata.get("slug")}-{os.path.basename(f.name)}')
                            workshop.save_slug()
                    except FileNotFoundError:
                        log.error(f'File `{workshopdata.get("image")}` could not be found. Did you run `python manage.py buildworkshop` before you ran this command?')
            else:
                workshop.image.name = get_default_workshop_image()
                workshop.save_slug()
                # TODO: Move warning to build stage
                log.warning(f'Workshop {workshopdata.get("name")} does not have an image assigned to them. Add filepaths to an existing file in your datafile ({DATAFILE}) if you want to update the specific workshop.')

            # 2. ENTER FRONTMATTER
            frontmatter, created = Frontmatter.objects.get_or_create(
                workshop=workshop)

            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Frontmatter for workshop `{workshop}` already exists. Update with new content? [y/N]')
                if choice.lower() != 'y':
                    continue

            Frontmatter.objects.filter(workshop=workshop).update(
                abstract=convert_html_quotes(frontmatterdata.get('abstract')),
                estimated_time=frontmatterdata.get('estimated_time')
            )

            frontmatter.refresh_from_db()

            for label in frontmatterdata.get('ethical_considerations'):
                _, created = EthicalConsideration.objects.get_or_create(frontmatter=frontmatter, label=convert_html_quotes(
                    label))  # convert_html_quotes here to make sure the curly quotes are found

            for label in frontmatterdata.get('learning_objectives'):
                _, created = LearningObjective.objects.get_or_create(frontmatter=frontmatter, label=convert_html_quotes(
                    label))  # convert_html_quotes here to make sure the curly quotes are found

            for projectdata in frontmatterdata.get('projects'):
                project, created = Resource.objects.update_or_create(
                    category=Resource.PROJECT, 
                    title=projectdata.get('title'), 
                    url=projectdata.get('url'), 
                    defaults={'annotation': projectdata.get('annotation')})
                frontmatter.projects.add(project)
                frontmatter.save()

            for readingdata in frontmatterdata.get('readings'):
                reading, created = Resource.objects.update_or_create(
                    category=Resource.READING, 
                    title=readingdata.get('title'), 
                    url=readingdata.get('url'), 
                    defaults={'annotation': readingdata.get('annotation')})
                frontmatter.readings.add(reading)
                frontmatter.save()

            for contributordata in frontmatterdata.get('contributors'):
                profile = Profile.objects.filter(user__first_name=contributordata.get(
                    'first_name'), user__last_name=contributordata.get('last_name'))
                if profile.count() == 1:
                    profile = profile[0]
                else:
                    profile = None

                contributor, created = Contributor.objects.get_or_create(
                    first_name=contributordata.get('first_name'), last_name=contributordata.get('last_name'))

                if not created and not options.get('forceupdate'):
                    choice = input.ask(
                        f'Contributor `{contributordata.get("first_name")} {contributordata.get("last_name")}` already exists. Update with new content? [y/N]')
                    if choice.lower() != 'y':
                        continue

                Contributor.objects.filter(first_name=contributordata.get('first_name'), last_name=contributordata.get('last_name')).update(
                    url=contributordata.get('url'),
                    profile=profile
                )

                contributor.refresh_from_db()

                collaboration, created = Collaboration.objects.get_or_create(
                    frontmatter=frontmatter, contributor=contributor)

                if not created and not options.get('forceupdate'):
                    choice = input.ask(
                        f'Collaboration between {contributor} and {workshop} already exists. Update with new content? [y/N]')
                    if choice.lower() != 'y':
                        continue

                Collaboration.objects.filter(frontmatter=frontmatter, contributor=contributor).update(
                    current=contributordata.get(
                        'collaboration').get('current'),
                    role=contributordata.get('collaboration').get('role')
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
                intro=praxisdata.get('intro'),
            )

            praxis.refresh_from_db()

            for questiondata in praxisdata.get('discussion_questions'):
                discussion_question, created = DiscussionQuestion.objects.get_or_create(praxis=praxis, label=convert_html_quotes(questiondata.get(
                    'label')), defaults={'order': questiondata.get('order')})  # convert_html_quotes here to make sure the curly quotes are found

                NextStep.objects.filter(praxis=praxis, label=convert_html_quotes(questiondata.get('label'))).update(
                    order=questiondata.get('order')
                )

                discussion_question.refresh_from_db()

            for stepdata in praxisdata.get('next_steps'):
                nextstep, created = NextStep.objects.get_or_create(praxis=praxis, label=convert_html_quotes(stepdata.get(
                    'label')), defaults={'order': stepdata.get('order')})  # convert_html_quotes here to make sure the curly quotes are found

                NextStep.objects.filter(praxis=praxis, label=convert_html_quotes(stepdata.get('label'))).update(
                    order=stepdata.get('order')
                )

                nextstep.refresh_from_db()

            for readingdata in praxisdata.get('further_readings'):
                '''
                # TODO: #280 make this into Resource instead + category = Resource.READING
                reading, created = Reading.objects.get_or_create(title=readingdata.get(
                    'title'), url=readingdata.get('url'), annotation=readingdata.get('annotation'))
                '''
                reading, created = Resource.objects.update_or_create(
                    category=Resource.READING,
                    title=readingdata.get('title'),
                    url=readingdata.get('url'),
                    defaults={'annotation': readingdata.get('annotation')})
                praxis.further_readings.add(reading)
                praxis.save()

            for projectdata in praxisdata.get('further_projects'):
                '''
                # TODO: #280 make this into Resource instead + category = Resource.PROJECT
                project, created = Project.objects.get_or_create(title=projectdata.get(
                    'title'), url=projectdata.get('url'), annotation=projectdata.get('annotation'))
                '''
                project, created = Resource.objects.update_or_create(
                    category=Resource.PROJECT, 
                    title=projectdata.get('title'), 
                    url=projectdata.get('url'), 
                    defaults={'annotation': projectdata.get('annotation')})
                praxis.further_projects.add(project)
                praxis.save()

            for tutorialdata in praxisdata.get('tutorials'):
                '''
                # TODO: #280 make this into Resource instead + category = Resource.TUTORIAL
                tutorial, created = Tutorial.objects.get_or_create(label=tutorialdata.get(
                    'label'), url=tutorialdata.get('url'), annotation=tutorialdata.get('annotation'))
                '''
                tutorial, created = Resource.objects.update_or_create(
                    category=Resource.TUTORIAL, 
                    title=tutorialdata.get('title'), 
                    url=tutorialdata.get('url'), 
                    defaults={'annotation': tutorialdata.get('annotation')})
                praxis.tutorials.add(tutorial)
                praxis.save()

            # 4. ENTER LESSONS

            for lessoninfo in lessondata:
                lesson, created = Lesson.objects.get_or_create(
                    workshop=workshop, title=lessoninfo.get('title'))

                if not created and not options.get('forceupdate'):
                    choice = input.ask(
                        f'Lesson `{lesson.title}` already exists. Update with new content? [y/N]')
                    if choice.lower() != 'y':
                        continue

                Lesson.objects.filter(workshop=workshop, title=lessoninfo.get('title')).update(
                    order=lessoninfo.get('order'),
                    text=lessoninfo.get('text'),
                )

                lesson.refresh_from_db()

                soup = BeautifulSoup(lesson.text, 'lxml')
                for img in soup.find_all('img'):
                    LessonImage.objects.update_or_create(url=img.get('src'), lesson=lesson)

                if not lessoninfo.get('challenge') and lessoninfo.get('solution'):
                    log.error(f'The workshop {workshop}\'s lesson `{lesson.title}` has a solution but no challenge. Correct the files on GitHub and rerun the buildworkshop command and then re-attempt the ingestworkshop command. Alternatively, you can change the datafile content manually.')

                if lessoninfo.get('challenge'):
                    challenge, created = Challenge.objects.get_or_create(lesson=lesson, title=lessoninfo.get(
                        'challenge_title'), text=convert_html_quotes(lessoninfo.get('challenge')))

                    if lessoninfo.get('solution'):
                        solution, created = Solution.objects.get_or_create(challenge=challenge, title=lessoninfo.get(
                            'solution_title'), text=convert_html_quotes(lessoninfo.get('solution')))

                for questioninfo in lessoninfo.get('questions'):
                    evaluation, created = Evaluation.objects.get_or_create(
                        lesson=lesson)
                    question, created = Question.objects.get_or_create(
                        evaluation=evaluation, label=convert_html_quotes(questioninfo.get('question'), strip_surrounding_body=False, strip_surrounding_p=True))
                    for answerinfo in questioninfo.get('answers', {}).get('correct'):
                        answer, created = Answer.objects.get_or_create(
                            question=question, label=convert_html_quotes(answerinfo), defaults={'is_correct': True})
                        answer.is_correct = True
                        answer.save()
                    for answerinfo in questioninfo.get('answers', {}).get('incorrect'):
                        answer, created = Answer.objects.get_or_create(
                            question=question, label=convert_html_quotes(answerinfo), defaults={'is_correct': False})
                        answer.is_correct = False
                        answer.save()

                for keyword in lessoninfo.get('keywords'):
                    finder = Term.objects.filter(term__iexact=keyword)
                    if finder.count() == 1:
                        lesson.terms.add(finder[0])
                        lesson.save()
                    elif finder.count() == 0:
                        log.warning(f'The keyword `{keyword}` used in workshop {workshop.name}\'s lesson {lesson.title} cannot be found in the glossary. Are you sure it is in the glossary and synchronized with the database? Make sure the data file for glossary is available ({GLOSSARY_FILE}) and that the term is defined in the file. Then run python manage.py ingestglossary.')
                    else:
                        log.error(
                            f'Multiple definitions of `{keyword}` exists in the database. Try resetting the glossary and rerun python manage.py ingestglossary before you run the ingestworkshop command again.')

        if default_workshop_image_exists() == False:
            log.warning(f'No default workshop image exists. Make sure the image with the path {get_default_workshop_image()} exists.')

        log.log('Added/updated workshops: ' +
                                 ', '.join([x[0] for x in workshops]))
        log.log(
            'Do not forget to run `ingestprerequisites` after running the `ingestworkshop` command (without the --name flag).', color='yellow')

        if log._save(data='ingestworkshop', name='warnings.md', warnings=True) or log._save(data='ingestworkshop', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' +
                    log.LOG_DIR, force=True)
