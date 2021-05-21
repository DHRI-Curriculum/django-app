from backend.dhri_utils import dhri_slugify
from install.models import OperatingSystem, Software, Instructions, Screenshot, Step
from django.core.management import BaseCommand
from django.core.files import File
from django.conf import settings
from backend.logger import Logger, Input
from ._shared_functions import test_for_required_files, get_yaml
import os
import filecmp


SAVE_DIR = f'{settings.BASE_DIR}/_preload/_install'
FULL_PATH = f'{SAVE_DIR}/install.yml'
REQUIRED_PATHS = [
    (SAVE_DIR,
     f'The required directory ({SAVE_DIR}) does not exist. Did you run `python manage.py buildinstalls` before you ran this command?'),
    (FULL_PATH,
     f'The required data file ({FULL_PATH}) does not exist. Did you run `python manage.py buildinstalls` before you ran this command?')
]


def get_software_image_path(image_file, relative_to_upload_field=False):
    if not relative_to_upload_field:
        return settings.MEDIA_ROOT + '/' + Software.image.field.upload_to + os.path.basename(image_file).replace('@', '')

    return Software.image.field.upload_to + os.path.basename(image_file).replace('@', '')

def get_screenshot_media_path(image_path, relative_to_upload_field=False):
    if not relative_to_upload_field:
        return settings.MEDIA_ROOT + '/' + Screenshot.image.field.upload_to + '/' + os.path.basename(image_path).replace('@', '')

    return Screenshot.image.field.upload_to + '/' + os.path.basename(image_path).replace('@', '')



def software_image_exists(image_file):
    return os.path.exists(get_software_image_path(image_file))


def get_default_software_image():
    return Software.image.field.default


def default_software_image_exists():
    return os.path.exists(get_default_software_image())


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with installs information into the database'
    requires_migrations_checks = True
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true')
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
            for operating_system_str in installdata.get('instructions'):
                
                # 0. Pre-process
                steps = installdata.get('instructions').get(operating_system_str)


                # 1. Create OperationSystem object
                
                # Standardize the operating systems (in `operating_system_str`)
                if 'windows' in operating_system_str.lower():
                    operating_system_str = 'windows'
                elif 'mac' in operating_system_str.lower():
                    operating_system_str = 'macos'
                else:
                    raise NotImplementedError(f'There is no way to import instructions for operating system {operating_system_str} currently. Add parsing in `ingestinstalls.py` if you want to build this operating system into the Curriculum website.')
                if OperatingSystem.objects.filter(slug=dhri_slugify(operating_system_str)):
                    operating_system = OperatingSystem.objects.get(slug=dhri_slugify(operating_system_str))
                else:
                    operating_system = OperatingSystem.objects.create(name=operating_system_str)
                

                # 2. Create Software object

                software, created = Software.objects.get_or_create(name=installdata.get('software'), defaults={
                    'what': installdata.get('what'),
                    'why': installdata.get('why')
                })

                original_file = installdata.get('image')
                if original_file:
                    if software_image_exists(original_file) and filecmp.cmp(original_file, get_software_image_path(original_file), shallow=False) == True:
                        log.log(f'Software image already exists. Ensuring path is in database: `{get_software_image_path(original_file)}`')
                        software.image.name = get_software_image_path(original_file, True)
                        software.save()
                    else:
                        with open(original_file, 'rb') as f:
                            software.image = File(f, name=os.path.basename(f.name))
                            software.save()
                        if filecmp.cmp(original_file, get_software_image_path(original_file)):
                            log.info(f'Software image has been updated so being copied to media path: `{get_software_image_path(original_file)}`')
                        else:
                            log.info(f'Software image has been copied to media path: `{get_software_image_path(original_file)}`')
                else:
                    log.warning(f'An image for `{software}` does not exist. A default image will be saved instead. If you want a particular image for the software, follow the documentation.')
                    software.image.name = get_default_software_image()
                    software.save()


                # 3. Create Instruction object

                instructions, created = Instructions.objects.get_or_create(operating_system=operating_system, software=software)


                # 4. Add Step objects

                for stepdata in steps:
                    step, created = Step.objects.update_or_create(
                        instructions=instructions,
                        order=stepdata.get('step'),
                        defaults={
                            'header': stepdata.get('header'),
                            'text': stepdata.get('html')
                        }
                    )

                    # 4b. Add screenshots for Step

                    for order, d in enumerate(stepdata.get('screenshots'), start=1):
                        path = d['path']
                        alt_text = d['alt']
                        if os.path.exists(get_screenshot_media_path(path)) and filecmp.cmp(path, get_screenshot_media_path(path), shallow=False) == True:
                            s, _ = Screenshot.objects.get_or_create(step=step, alt_text=alt_text, order=order)
                            s.image = get_screenshot_media_path(path, relative_to_upload_field=True)
                            s.save()
                            log.log(f'Screenshot already exists: `{get_screenshot_media_path(path)}`')
                        else:
                            s, _ = Screenshot.objects.get_or_create(step=step, alt_text=alt_text, order=order)
                            with open(path, 'rb') as f:
                                s.image = File(f, name=os.path.basename(f.name))
                                s.save()
                            if filecmp.cmp(path, get_screenshot_media_path(path), shallow=False) == False:
                                log.log(f'Screenshot was updated so re-saved: `{get_screenshot_media_path(path)}`')
                            else:
                                log.log(f'New screenshot saved: `{get_screenshot_media_path(path)}`')

        log.log('Added/updated installation instructions: ' +
                                 ', '.join([f'{x["software"]}' for x in data]))

        if log._save(data='ingestinstalls', name='warnings.md', warnings=True) or log._save(data='ingestinstalls', name='logs.md', warnings=False, logs=True) or log._save(data='ingestinstalls', name='info.md', warnings=False, logs=False, info=True):
            log.log(f'Log files with any warnings and logging information is now available in: `{log.LOG_DIR}`', force=True)