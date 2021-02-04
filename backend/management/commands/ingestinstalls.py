from backend.mixins import convert_html_quotes
from install.models import Software, Instruction, Screenshot, Step
from django.core.management import BaseCommand
from django.core.files import File
from django.conf import settings
from backend.dhri.log import Logger, Input
from ._shared import test_for_required_files, get_yaml, LogSaver
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


def get_instruction_image_path(image_file, relative_to_upload_field=False):
    if not relative_to_upload_field:
        return settings.MEDIA_ROOT + '/' + Instruction.image.field.upload_to + os.path.basename(image_file).replace('@', '')

    return Instruction.image.field.upload_to + os.path.basename(image_file).replace('@', '')


def instruction_image_exists(image_file):
    return os.path.exists(get_instruction_image_path(image_file))


def get_default_instruction_image():
    return Instruction.image.field.upload_to + Instruction.image.field.default


def default_instruction_image_exists():
    return os.path.exists(get_default_instruction_image())


class Command(LogSaver, BaseCommand):
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

            original_file = installdata.get('instruction', {}).get('image')
            if original_file:
                if instruction_image_exists(original_file):
                    instruction.image.name = get_instruction_image_path(
                        original_file, True)
                    instruction.save()
                else:
                    with open(original_file, 'rb') as f:
                        instruction.image = File(
                            f, name=os.path.basename(f.name))
                        instruction.save()
            else:
                instruction.image.name = get_default_instruction_image()
                instruction.save()
                # TODO: Move warning to build stage
                self.WARNINGS.append(log.warning(
                    f'Installation instruction for {installdata.get("software")} does not have an image assigned to them. Add filepaths to an existing file in your datafile ({FULL_PATH}) if you want to update the specific instruction image.'))

            for stepdata in installdata.get('instruction', {}).get('steps', []):
                step, created = Step.objects.get_or_create(
                    instruction=instruction, order=stepdata.get('order'), defaults={'header': stepdata.get('header'), 'text': convert_html_quotes(stepdata.get('text'))})

                if not created and not options.get('forceupdate'):
                    choice = input.ask(
                        f'Step {stepdata.get("order")} for installation of `{installdata.get("software")}` (with OS `{installdata.get("operating_system")}`) seems to already exist. Update with new instructions? [y/N]')
                    if choice.lower() != 'y':
                        continue

                Step.objects.filter(instruction=instruction, order=stepdata.get('order')).update(
                    header=stepdata.get('header'), text=stepdata.get('text'),
                )

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

        self.LOGS.append(log.log('Added/updated installation instructions: ' +
                                 ', '.join([f'{x.get("software")} ({x.get("operating_system")})' for x in data])))

        self.SAVE_DIR = self.SAVE_DIR = f'{LogSaver.LOG_DIR}/ingestinstalls'
        if self._save(data='ingestinstalls', name='warnings.md', warnings=True) or self._save(data='ingestinstalls', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' +
                    self.SAVE_DIR, force=True)
