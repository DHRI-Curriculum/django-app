from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger
from backend.dhri.install_parser import InstallLoader
from ._shared import get_name, LogSaver
from shutil import copyfile
import re
import pathlib
import yaml


SAVE_DIR = f'{settings.BASE_DIR}/_preload/_install'
DATA_FILE = 'install.yml'


class Command(LogSaver, BaseCommand):
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
        log = Logger(name=get_name(__file__), force_verbose=options.get('verbose'), force_silent=options.get('silent'))

        log.log('Building installation instruction files... Please be patient as this can take some time.')

        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        loader = InstallLoader(force_download=options.get('forcedownload'))
        installs = list()

        for software in loader.all_software:
            instructions = loader.instructions.get(software)
            operating_systems = {
                'Windows': instructions.windows, 'macOS': instructions.mac_os}
            for o_s, current_instructions in operating_systems.items():
                if current_instructions:
                    install = {
                        'software': software,
                        'operating_system': o_s,
                        'instruction': {
                            'what': instructions.what.strip(),
                            'why': instructions.why.strip(),
                            'image': instructions.image_path,
                            'steps': []
                        }
                    }
                    for _, d in current_instructions.items():
                        step = {
                            'order': d.get('order'),
                            'text': d.get('html'),
                            'header': d.get('header'),
                            'screenshots': []
                        }

                        for screenshot in d.get('screenshots'):
                            copyfile(screenshot[1], f'{SAVE_DIR}/images/{screenshot[0]}')
                            step['screenshots'].append(f'{SAVE_DIR}/images/{screenshot[0]}')

                        install['instruction']['steps'].append(step)
                installs.append(install)

        # Save all data
        with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
            file.write(yaml.dump(installs))

        self.LOGS.append(log.log(f'Saved installs datafile: {SAVE_DIR}/{DATA_FILE}.'))
            
        self.SAVE_DIR = self.SAVE_DIR = f'{LogSaver.LOG_DIR}/buildinstalls'
        if self._save(data='buildinstalls', name='warnings.md', warnings=True) or self._save(data='buildinstalls', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' + self.SAVE_DIR, force=True)
