from glossary.models import Term
from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger, Input
from ._shared import test_for_required_files, get_yaml, get_name, LogSaver


SAVE_DIR = f'{settings.BASE_DIR}/_preload/_meta/glossary'
FULL_PATH = f'{SAVE_DIR}/glossary.yml'
REQUIRED_PATHS = [
    (SAVE_DIR, f'The required directory ({SAVE_DIR}) does not exist. Did you run `python manage.py buildglossary` before you ran this command?'),
    (FULL_PATH, f'The required data file ({FULL_PATH}) does not exist. Did you run `python manage.py buildglossary` before you ran this command?')
]


class Command(LogSaver, BaseCommand):
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
        log = Logger(name=get_name(__file__), force_verbose=options.get('verbose'), force_silent=options.get('silent'))
        input = Input(name=get_name(__file__))
        test_for_required_files(REQUIRED_PATHS=REQUIRED_PATHS, log=log)
        data = get_yaml(f'{FULL_PATH}')

        for termdata in data:
            term, created = Term.objects.get_or_create(term=termdata.get('term'))

            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Term `{termdata.get("term")}` already exists. Update with new definition? [y/N]')
                if choice.lower() != 'y':
                    continue
            
            Term.objects.filter(term=termdata.get('term')).update(
                explication=termdata.get('explication')
            )

        self.LOGS.append(log.log('Added/updated terms: ' + ', '.join([x.get('term') for x in data])))
            
        self.SAVE_DIR = self.SAVE_DIR = f'{LogSaver.LOG_DIR}/buildusers'
        if self._save(data='buildusers', name='warnings.md', warnings=True) or self._save(data='buildusers', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' + self.SAVE_DIR, force=True)
