from backend.mixins import convert_html_quotes
from glossary.models import Term
from resource.models import Resource
from django.core.management import BaseCommand
from django.conf import settings
from backend.logger import Logger, Input
from ._shared import test_for_required_files, get_yaml


SAVE_DIR = f'{settings.BASE_DIR}/_preload/_meta/glossary'
FULL_PATH = f'{SAVE_DIR}/glossary.yml'
REQUIRED_PATHS = [
    (SAVE_DIR,
     f'The required directory ({SAVE_DIR}) does not exist. Did you run `python manage.py buildglossary` before you ran this command?'),
    (FULL_PATH,
     f'The required data file ({FULL_PATH}) does not exist. Did you run `python manage.py buildglossary` before you ran this command?')
]


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with glossary information into the database'
    requires_migrations_checks = True
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
                     force_verbose=options.get('verbose'),
                     force_silent=options.get('silent')
                     )
        input = Input(path=__file__)

        test_for_required_files(REQUIRED_PATHS=REQUIRED_PATHS, log=log)
        data = get_yaml(f'{FULL_PATH}')

        for termdata in data:
            term, created = Term.objects.get_or_create(
                term=termdata.get('term'))

            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Term `{termdata.get("term")}` already exists. Update with new definition? [y/N]')
                if choice.lower() != 'y':
                    continue

            Term.objects.filter(term=termdata.get('term')).update(
                explication=termdata.get('explication')
            )

            term.refresh_from_db()

            if termdata.get('projects'):
                for projectdata in termdata.get('projects'):
                    project, created = Resource.objects.get_or_create(
                        category=Resource.PROJECT,
                        annotation=projectdata.get('annotation'),
                        title=projectdata.get('linked_text'),
                        url=projectdata.get('url')
                    )
                    term.projects.add(project)
                    term.save()

            if termdata.get('tutorials'):
                for tutorialdata in termdata.get('tutorials'):
                    tutorial, created = Resource.objects.get_or_create(
                        category=Resource.TUTORIAL,
                        annotation=tutorialdata.get('annotation'),
                        title=tutorialdata.get('linked_text'),
                        url=tutorialdata.get('url')
                    )
                    term.tutorials.add(tutorial)
                    term.save()

        log.log('Added/updated terms: ' +
                                 ', '.join([x.get('term') for x in data]))

        if log._save(data='buildusers', name='warnings.md', warnings=True) or log._save(data='buildusers', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' +
                    log.LOG_DIR, force=True)
