from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger
from backend import dhri_settings
from ._shared import get_name
import yaml
import pathlib

DATA_FILE = 'blurb.yml'


def find_dir(workshop):
    TEST_DIR = f'{settings.BASE_DIR}/_preload/_workshops/{workshop}'
    if pathlib.Path(TEST_DIR).exists():
        return TEST_DIR

    return False


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from blurbs (provided through AUTO_USERS in backend.dhri_settings)'

    def add_arguments(self, parser):
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(name=get_name(__file__), force_verbose=options.get('verbose'), force_silent=options.get('silent'))

        log.log('Building blurbs...')

        for cat in list(dhri_settings.AUTO_USERS.keys()):
            for u in dhri_settings.AUTO_USERS[cat]:
                if u.get('blurb'):
                    text = u.get(
                        'blurb', {'text': None, 'workshop': None}).get('text')
                    workshop = u.get(
                        'blurb', {'text': None, 'workshop': None}).get('workshop')
                    if text and workshop:
                        SAVE_DIR = f'{settings.BASE_DIR}/_preload/_workshops/{workshop}'

                        if find_dir(workshop):
                            with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
                                file.write(yaml.dump({
                                    'workshop': workshop,
                                    'user': u.get('username'),
                                    'text': text
                                }))
                            
                            log.log(f'Saved blurb datafile: {SAVE_DIR}/{DATA_FILE}.')
                        else:
                            log.error(f'No directory available for `{workshop}` ({SAVE_DIR}). Did you run `python manage.py build --repo {workshop}` before running this script?', kill=True)
