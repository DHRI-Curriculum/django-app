from insight.models import Insight, OperatingSystemSpecificSection, Section
from django.core.management import BaseCommand
from django.core.files import File
from django.conf import settings
from backend.logger import Logger, Input
from ._shared_functions import test_for_required_files, get_yaml

import os
import filecmp

SAVE_DIR = f'{settings.BASE_DIR}/_preload/_insights'
FULL_PATH = f'{SAVE_DIR}/insights.yml'
REQUIRED_PATHS = [
    (SAVE_DIR,
     f'The required directory ({SAVE_DIR}) does not exist. Did you run `python manage.py buildinstalls` before you ran this command?'),
    (FULL_PATH,
     f'The required data file ({FULL_PATH}) does not exist. Did you run `python manage.py buildinstalls` before you ran this command?')
]


def get_insight_image_path(image_file, relative_to_upload_field=False):
    if not relative_to_upload_field:
        return settings.MEDIA_ROOT + '/' + Insight.image.field.upload_to + os.path.basename(image_file).replace('@', '')

    return Insight.image.field.upload_to + os.path.basename(image_file).replace('@', '')


def insight_image_exists(image_file):
    return os.path.exists(get_insight_image_path(image_file))


def get_default_insight_image():
    return Insight.image.field.default


class Command(BaseCommand):
    import os

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with insights information into the database'
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

        for insightdata in data:
            # TODO: Insights and Software are also connected in a database table (insight_insight_software) but this relationship is not developed yet.
            insight, created = Insight.objects.update_or_create(
                title=insightdata.get('insight'), defaults={
                    'text': insightdata.get('introduction'),
                    'image_alt': insightdata.get('image').get('alt')
                }
            )
            
            original_file = insightdata.get('image').get('url')
            if original_file:
                if insight_image_exists(original_file) and filecmp.cmp(original_file, get_insight_image_path(original_file), shallow=False) == True:
                    log.log(f'Insight image already exists. Connecting existing paths to database: `{get_insight_image_path(original_file)}`')
                    insight.image.name = get_insight_image_path(original_file, True)
                    insight.save()
                else:
                    with open(original_file, 'rb') as f:
                        insight.image = File(f, name=self.os.path.basename(f.name))
                        insight.save()

                    if filecmp.cmp(original_file, get_insight_image_path(original_file), shallow=False):
                        log.info(f'Insight image has been updated and thus was copied to the media path: `{get_insight_image_path(original_file)}`')
                    else:
                        log.info(f'Insight image was not found and is copied to media path: `{get_insight_image_path(original_file)}`')
            else:
                log.warning(f'An image for `{insight}` does not exist. A default image will be saved instead. If you want a particular image for the installation instructions, follow the documentation.')
                insight.image.name = get_default_insight_image()
                insight.save()
            
            for sectiondata in insightdata.get('sections', []):
                title = sectiondata
                sectiondata = insightdata.get('sections').get(sectiondata)
                section, created = Section.objects.update_or_create(insight=insight, title=title, defaults={'order': sectiondata.get('order'), 'text': sectiondata.get('content')})

            for operating_system, osdata in insightdata.get('os_specific').items():
                related_section = Section.objects.get(title=osdata.get('related_section'))

                OperatingSystemSpecificSection.objects.update_or_create(
                    section=related_section,
                    operating_system=operating_system,
                    defaults={
                        'text': osdata.get('content')
                    }
                )

        log.log('Added/updated insights: ' +
                                 ', '.join([x.get("insight") for x in data]))

        if log._save(data='ingestinsights', name='warnings.md', warnings=True) or log._save(data='ingestinsights', name='logs.md', warnings=False, logs=True) or log._save(data='ingestinsights', name='info.md', warnings=False, logs=False, info=True):
            log.log(f'Log files with any warnings and logging information is now available in: `{log.LOG_DIR}`', force=True)