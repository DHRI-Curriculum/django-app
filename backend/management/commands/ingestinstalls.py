from install.models import Software, Instruction, Screenshot, Step
from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger, Input
from backend.mixins import convert_html_quotes
from ._shared import test_for_required_files, get_yaml, get_name
from shutil import copyfile
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


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with installs information into the database'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(name=get_name(__file__), force_verbose=options.get('verbose'), force_silent=options.get('silent'))
        input = Input(name=get_name(__file__))
        test_for_required_files(REQUIRED_PATHS=REQUIRED_PATHS, log=log)
        data = get_yaml(f'{FULL_PATH}')

        for installdata in data:
            software, created = Software.objects.get_or_create(operating_system=installdata.get(
                'operating_system'), software=installdata.get('software'))
            instruction, created = Instruction.objects.get_or_create(
                software=software)

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
                path = f'{settings.BASE_DIR}/website/{installdata.get("instruction", {}).get("image")}'
                if os.path.exists(path):
                    pass  # log.log('image is already in place')
                else:
                    log.error(
                        f'Unfortunately, the image `{os.path.basename(path)}` cannot be found in the correct directory ({os.path.dirname(path)}). You need to place the file there manually.')
            else:
                log.error(
                    f'Installation instructions for `{installdata.get("software")}` (with OS `{installdata.get("operating_system")}`) is missing an image. Add a filepath to an existing file in your datafile ({FULL_PATH}) to be able to run this command.')

            for stepdata in installdata.get('instruction', {}).get('steps', []):
                # TODO: rewrite this below with convert_html_quotes...
                step = Step.objects.filter(
                    instruction=instruction, order=stepdata.get('order'))
                if step.count() == 1:
                    step = step.last()
                    step.text = stepdata.get('text')
                    step.header = stepdata.get('header')
                    step.save()
                elif step.count() == 0:
                    step = Step.objects.create(instruction=instruction, order=stepdata.get(
                        'order'), text=stepdata.get('text'), header=stepdata.get('header'))
                else:
                    log.error(
                        'Too many identical installation steps! Try resetting and re-run python manage.py ingestinstalls.')

                for order, path in enumerate(stepdata.get('screenshots'), start=1):
                    screenshot = Screenshot.objects.filter(
                        step=step, image='installation_screenshots/'+os.path.basename(path))
                    if screenshot.count() == 1:
                        screenshot = screenshot.last()
                    elif screenshot.count() == 0:
                        # print('does not exist')
                        screenshot = Screenshot.objects.create(
                            step=step, order=order)
                        if not screenshot_exists(get_screenshot_path(path, True)):
                            copyfile(path, get_screenshot_path(path))
                        screenshot.image.name = get_screenshot_path(path, True)
                        screenshot.save()
                    else:
                        log.error(
                            'Too many identical screenshots. Try resetting and re-run python manage.py ingestinstalls.')

        log.log('Added/updated installation instructions: ' +
                ', '.join([f'{x.get("software")} ({x.get("operating_system")})' for x in data]))
