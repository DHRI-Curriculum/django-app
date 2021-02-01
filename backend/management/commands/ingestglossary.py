from glossary.models import Term
from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger, Input
from ._shared import test_for_required_files, get_yaml, get_name


log = Logger(name=get_name(__file__))
input = Input(name=get_name(__file__))
SAVE_DIR = f'{settings.BASE_DIR}/_preload/_meta/glossary'
FULL_PATH = f'{SAVE_DIR}/glossary.yml'
REQUIRED_PATHS = [
    (SAVE_DIR, f'The required directory ({SAVE_DIR}) does not exist. Did you run `python manage.py buildglossary` before you ran this command?'),
    (FULL_PATH, f'The required data file ({FULL_PATH}) does not exist. Did you run `python manage.py buildglossary` before you ran this command?')
]


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with glossary information into the database'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')

    def handle(self, *args, **options):
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

        log.log('Added/updated terms: ' + ', '.join([x.get('term') for x in data]))
