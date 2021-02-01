from website.models import Snippet
from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger, Input
from ._shared import test_for_required_files, get_yaml, get_name


log = Logger(name=get_name(__file__))
input = Input(name=get_name(__file__))
SAVE_DIR = f'{settings.BASE_DIR}/_preload'
FULL_PATH = f'{SAVE_DIR}/snippets.yml' # TODO: change to SNIPPET_SETUP
REQUIRED_PATHS = [
    (SAVE_DIR, f'The required directory ({SAVE_DIR}) does not exist. This directory can be created manually if need be.'),
    (FULL_PATH, f'The required data file ({FULL_PATH}) does not exist. This file needs to be created manually. See the instrcuctions for its structure.')
]


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with snippet information into the database'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')

    def handle(self, *args, **options):
        test_for_required_files(REQUIRED_PATHS=REQUIRED_PATHS, log=log)
        data = get_yaml(f'{FULL_PATH}')

        for identifier, snippetdata in data.items():
            snippet, created = Snippet.objects.get_or_create(identifier=identifier)
            
            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Snippet `{identifier}` already exists. Update with new definition? [y/N]')
                if choice.lower() != 'y':
                    continue
            
            Snippet.objects.filter(identifier=identifier).update(
                snippet=snippetdata
            )

        log.log('Added/updated snippets: ' + ', '.join([x for x in data]))
