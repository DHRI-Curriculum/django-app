from backend.github import InstallCache
from django.core.management import BaseCommand
from django.conf import settings
from backend.logger import Logger
# from backend.dhri.install_parser import InstallLoader

from shutil import copyfile
import re
import pathlib
import yaml


SAVE_DIR = f'{settings.BASE_DIR}/_preload/_install'
SAVE_DIR_IMAGES = f'{settings.BASE_DIR}/_preload/_install/images'
DATA_FILE = 'install.yml'


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from install repository'
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--forcedownload', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
            force_verbose=options.get('verbose'),
            force_silent=options.get('silent')
        )

        log.log(
            'Building installation instruction files... Please be patient as this can take some time.')

        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        if not pathlib.Path(SAVE_DIR_IMAGES).exists():
            pathlib.Path(SAVE_DIR_IMAGES).mkdir(parents=True)

        # loader = InstallLoader(force_download=options.get('forcedownload')) # TODO: #406
        loader = InstallCache(log=log)
        installs = list()

        for install_data in loader.data:
            installs.append(install_data)

        # Save all data
        with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
            file.write(yaml.dump(installs))

        log.log(f'Saved installs datafile: {SAVE_DIR}/{DATA_FILE}.')

        if log._save(data='buildinstalls', name='warnings.md', warnings=True) or log._save(data='buildinstalls', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' +
                    log.LOG_DIR, force=True)
