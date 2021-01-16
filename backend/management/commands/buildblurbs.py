from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger
from .imports import *
from backend import dhri_settings
import yaml
import pathlib

log = Logger(name='build-blurbs')
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

    def handle(self, *args, **options):
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
                        else:
                            log.error(f'No directory available for `{workshop}` ({SAVE_DIR}). Did you run `python manage.py build --repo {workshop}` before running this script?', kill=True)
