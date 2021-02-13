from install.models import Software, Instruction, Screenshot, Step
from django.core.management import BaseCommand
from django.core.files import File
from django.conf import settings
from backend.logger import Logger, Input
from ._shared_functions import test_for_required_files, get_yaml
import os


SAVE_DIR = f'{settings.BASE_DIR}/_preload/_install'
FULL_PATH = f'{SAVE_DIR}/install.yml'
REQUIRED_PATHS = [
    (SAVE_DIR,
     f'The required directory ({SAVE_DIR}) does not exist. Did you run `python manage.py buildinstalls` before you ran this command?'),
    (FULL_PATH,
     f'The required data file ({FULL_PATH}) does not exist. Did you run `python manage.py buildinstalls` before you ran this command?')
]


def get_screenshot_path(image_file, relative_to_upload_field=False):
    if not relative_to_upload_field:
        return settings.MEDIA_ROOT + '/' + Screenshot.image.field.upload_to + '/' + os.path.basename(image_file)

    return Screenshot.image.field.upload_to + '/' + os.path.basename(image_file)


def screenshot_exists(image_file):
    return os.path.exists(get_screenshot_path(image_file))


def get_instruction_image_path(image_file, relative_to_upload_field=False):
    if not relative_to_upload_field:
        return settings.MEDIA_ROOT + '/' + Instruction.image.field.upload_to + os.path.basename(image_file).replace('@', '')

    return Instruction.image.field.upload_to + os.path.basename(image_file).replace('@', '')


def instruction_image_exists(image_file):
    return os.path.exists(get_instruction_image_path(image_file))


def get_default_instruction_image():
    return Instruction.image.field.default


def default_instruction_image_exists():
    return os.path.exists(get_default_instruction_image())


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with installs information into the database'
    requires_migrations_checks = True
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
                     force_verbose=options.get('verbose'),
                     force_silent=options.get('silent')
                     )
        input = Input(path=__file__)

        test_for_required_files(REQUIRED_PATHS=REQUIRED_PATHS, log=log)
        data = get_yaml(FULL_PATH, log=log)

        for installdata in data:
            for operating_system in installdata.get('instructions'):
                software, created = Software.objects.get_or_create(operating_system=operating_system, software=installdata.get('software'))
                instruction, created = Instruction.objects.update_or_create(software=software, defaults={
                    'what': installdata.get('what'),
                    'why': installdata.get('why')
                })

                original_file = installdata.get('image')
                if original_file:
                    if instruction_image_exists(original_file):
                        log.log(f'Instruction image already exists. Adding path: `{os.path.basename(original_file)}`')
                        instruction.image.name = get_instruction_image_path(
                            original_file, True)
                        instruction.save()
                    else:
                        log.info(f'Instruction image is being copied to media path: `{os.path.basename(original_file)}`')
                        with open(original_file, 'rb') as f:
                            instruction.image = File(f, name=os.path.basename(f.name))
                            instruction.save()
                else:
                    log.warning(f'An image for `{software}` does not exist. A default image will be saved instead. If you want a particular image for the installation instructions, follow the documentation.')
                    instruction.image.name = get_default_instruction_image()
                    instruction.save()
                    
            for stepdata in installdata.get('instructions').get(operating_system):
                step, created = Step.objects.update_or_create(
                    instruction=instruction,
                    order=stepdata.get('step'),
                    defaults={
                        'header': stepdata.get('header'),
                        'text': stepdata.get('html')
                    }
                )

                for order, d in enumerate(stepdata.get('screenshots'), start=1):
                    path = d['path']
                    alt_text = d['alt']
                    Screenshot.objects.update_or_create(
                        image='installation_screenshots/'+os.path.basename(path), defaults={'order': order, 'step': step, 'alt_text': alt_text})

        log.log('Added/updated installation instructions: ' +
                                 ', '.join([f'{x["software"]}' for x in data]))

        if log._save(data='ingestinstalls', name='warnings.md', warnings=True) or log._save(data='ingestinstalls', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' +
                    log.LOG_DIR, force=True)
