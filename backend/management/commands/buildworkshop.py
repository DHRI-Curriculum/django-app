from backend.github import WorkshopCache
from django.core.management import BaseCommand
from backend.logger import Logger
from backend import settings

import yaml
import pathlib

def check_for_cancel(SAVE_DIR, workshop, log=None):
    if pathlib.Path(SAVE_DIR).exists():
        _ = input(f'{workshop} already exists. Replace? [n/Y]')
        if _ == '' or _.lower() == 'y':
            pass
        else:
            if not log:
                exit('User exit.')
            else:
                log.error('User exit.')


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from workshops in the GitHub repository (provided through --workshop parameter)'
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Automatically approves any requests to replace/update existing local data.')
        parser.add_argument('--save_all', action='store_true')
        parser.add_argument('--silent', action='store_true',
                            help='Makes as little output as possible, although still saves all the information in log files (see debugging docs).')
        parser.add_argument('--verbose', action='store_true',
                            help='Provides all output possible, which can be overwhelming. Good for debug purposes, not for the faint of heart.')

        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument('--name', nargs='+', type=str,
                           help='Provide a specific name of a workshop to build.')
        group.add_argument('--all', action='store_true',
                           help='Build all workshop datafiles.')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
                     force_verbose=options.get('verbose'),
                     force_silent=options.get('silent')
                     )

        if options.get('all'):
            options['name'] = [x[0] for x in settings.AUTO_REPOS]

        if not options.get('name'):
            log.error(
                'No workshop names provided. Use any of the following settings:\n    --name [repository name]\n    --all')

        log.log(
            'Building workshop files... Please be patient as this can take some time.')

        for workshop in options.get('name'):
            SAVE_DIR = f'{settings.BUILD_DIR}_workshops/{workshop}'
            DATA_FILE = f'{workshop}.yml'
            if not options.get('force'):
                check_for_cancel(SAVE_DIR, workshop, log=log)

            if not pathlib.Path(SAVE_DIR).exists():
                pathlib.Path(SAVE_DIR).mkdir(parents=True)

            branch = 'v2.0'  # TODO: fix this...
            loader = WorkshopCache(repository=workshop, branch=branch, log=log)
            data = loader.data
            del data['raw']
            data['sections'] = loader.sections
            data['parent_branch'] = loader.branch
            data['parent_repo'] = workshop
            data['parent_backend'] = 'Github'

            # Save all data
            with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
                file.write(yaml.dump(data))

                log.log(f'Saved workshop datafile: `{SAVE_DIR}/{DATA_FILE}`')

            if log._save(data=workshop, name='warnings.md', warnings=True) or log._save(data=workshop, name='logs.md', warnings=False, logs=True) or log._save(data=workshop, name='info.md', warnings=False, logs=False, info=True):
                log.log(
                    'Log files with any warnings and logging information is now available in the' + log.LOG_DIR, force=True)