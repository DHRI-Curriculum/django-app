from django.core.management import BaseCommand
from backend.logger import Logger
from backend import settings

import yaml
import pathlib

SAVE_DIR = f'{settings.BUILD_DIR}_meta/users'
DATA_FILE = 'groups.yml'


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from groups information (provided through backend.settings.AUTO_GROUPS)'
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

        log.log('Building group files... Please be patient as this can take some time.')

        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        permissions = {}

        for group_name in settings.AUTO_GROUPS:
            permissions[group_name] = list()
            for model_cls in settings.AUTO_GROUPS[group_name]:
                for perm_name in settings.AUTO_GROUPS[group_name][model_cls]:
                    # Generate permission name as Django would generate it
                    codename = perm_name + '_' + model_cls._meta.model_name
                    permissions[group_name].append(codename)

        # Save all data
        with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
            file.write(yaml.dump(permissions))

        log.log(f'Saved groups data file: {SAVE_DIR}/{DATA_FILE}')

        if log._save(data='buildgroups', name='warnings.md', warnings=True) or log._save(data='buildgroups', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' +
                    log.LOG_DIR, force=True)
