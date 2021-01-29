from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger, Input
from .imports import Software, Instruction
from ._shared import test_for_required_files, get_yaml, get_name

import yaml
import pathlib

log = Logger(name=get_name(__file__))
input = Input(name=get_name(__file__))
SAVE_DIR = f'{settings.BASE_DIR}/_preload/_install'
FULL_PATH = f'{SAVE_DIR}/install.yml'
REQUIRED_PATHS = [
    (SAVE_DIR, f'The required directory ({SAVE_DIR}) does not exist. Did you run `python manage.py buildinstalls` before you ran this command?'),
    (FULL_PATH, f'The required data file ({FULL_PATH}) does not exist. Did you run `python manage.py buildinstalls` before you ran this command?')
]


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with installs information into the database'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')

    def handle(self, *args, **options):
        test_for_required_files(REQUIRED_PATHS=REQUIRED_PATHS, log=log)
        data = get_yaml(f'{FULL_PATH}')

        for installdata in data:
            software, created = Software.objects.get_or_create(operating_system=installdata.get('operating_system'), software=installdata.get('software'))
            instruction, created = Instruction.objects.get_or_create(software=software)
            
            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Installation instructions for `{installdata.get("software")}` (with OS `{installdata.get("operating_system")}`) already exists. Update with new instructions? [y/N]')
                if choice.lower() != 'y':
                    continue
            
            Instruction.objects.filter(software=software).update(
                what=installdata.get('instruction', {}).get('what'),
                why=installdata.get('instruction', {}).get('why')
            )

            instruction.refresh_from_db()

            if installdata.get('instruction', {}).get('image'):
                # TODO: This needs to be fixed, once we're in a computer where we can write to this directory
                print(installdata.get('instruction', {}).get('image'))
                exit(instruction.image.name)
            else:
                log.error(f'Installation instructions for `{installdata.get("software")}` (with OS `{installdata.get("operating_system")}`) is missing an image. Add a filepath to an existing file in your datafile ({FULL_PATH}) to be able to run this command.')

        # log.log('Added/updated terms: ' + ', '.join([x.get('term') for x in data]))
