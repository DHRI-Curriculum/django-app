from backend.markdown_parser import PARSER
from django.core.management import BaseCommand
from backend.logger import Logger
from backend import settings

import yaml
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

    help = 'Build YAML files from blurbs (provided through AUTO_USERS in backend.settings)'
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
            force_verbose=options.get('verbose'),
            force_silent=options.get('silent')
        )

        log.log('Building blurbs... Please be patient as this can take some time.')

        for cat in list(settings.AUTO_USERS.keys()):
            for u in settings.AUTO_USERS[cat]:
                if u.get('blurb'):
                    text = u.get(
                        'blurb', {'text': None, 'workshop': None}).get('text')
                    workshop = u.get(
                        'blurb', {'text': None, 'workshop': None}).get('workshop')
                    if text and workshop:
                        SAVE_DIR = f'{settings.BUILD_DIR}_workshops/{workshop}'

                        if find_dir(workshop):
                            with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
                                file.write(yaml.dump({
                                    'workshop': workshop,
                                    'user': u.get('username'),
                                    'text': PARSER.fix_html(text)
                                }))

                                log.log(f'Saved blurb datafile: {SAVE_DIR}/{DATA_FILE}.')
                        else:
                            log.error(
                                f'No directory available for `{workshop}` ({SAVE_DIR}). Did you run `python manage.py build --repo {workshop}` before running this script?', kill=True)

        if log._save(data='buildblurbs', name='warnings.md', warnings=True) or log._save(data='buildblurbs', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' +
                    log.LOG_DIR, force=True)
