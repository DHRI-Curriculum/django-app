from django.core.management import BaseCommand, call_command
from backend.logger import Logger
from backend import settings

import os
import pathlib

DATA_FILE = 'blurb.yml'


def find_dir(workshop):
    TEST_DIR = f'{settings.BUILD_DIR}_workshops/{workshop}'
    if pathlib.Path(TEST_DIR).exists():
        return TEST_DIR

    return False


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Clears out all the migration files and rebuilds them (with the --rebuild flag)'
    
    def add_arguments(self, parser):
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--rebuild', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
            force_verbose=options.get('verbose'),
            force_silent=options.get('silent')
        )

        log.log('Removing migration files...')

        os.system('find . -path "*/migrations/*.py" -not -name "__init__.py" -delete && find . -path "*/migrations/*.pyc"  -delete && git pull')

        call_command('makemigrations')
        call_command('migrate')