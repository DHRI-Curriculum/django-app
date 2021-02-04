from insight.models import Insight, OperatingSystemSpecificSection, Section
from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger, Input
from backend.mixins import convert_html_quotes
from ._shared import test_for_required_files, get_yaml, LogSaver


SAVE_DIR = f'{settings.BASE_DIR}/_preload/_insights'
FULL_PATH = f'{SAVE_DIR}/insights.yml'
REQUIRED_PATHS = [
    (SAVE_DIR,
     f'The required directory ({SAVE_DIR}) does not exist. Did you run `python manage.py buildinstalls` before you ran this command?'),
    (FULL_PATH,
     f'The required data file ({FULL_PATH}) does not exist. Did you run `python manage.py buildinstalls` before you ran this command?')
]


class Command(LogSaver, BaseCommand):
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
        log = Logger(path=__file__, force_verbose=options.get('verbose'), force_silent=options.get('silent'))
        input = Input(path=__file__)
        test_for_required_files(REQUIRED_PATHS=REQUIRED_PATHS, log=log)
        data = get_yaml(f'{FULL_PATH}')

        for insightdata in data:
            insight, created = Insight.objects.get_or_create(title=insightdata.get('title'), defaults={
                'text': convert_html_quotes(insightdata.get('text'))
            })

            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Insight `{insightdata.get("title")}` already exists. Update with new content? [y/N]')
                if choice.lower() != 'y':
                    continue

            Insight.objects.filter(title=insightdata.get('title')).update(text=convert_html_quotes(insightdata.get('text')))

            for sectiondata in insightdata.get('sections', []):
                section, created = Section.objects.get_or_create(insight=insight, title=sectiondata.get(
                    'title'), defaults={'order': sectiondata.get('order'), 'text': sectiondata.get('text')})

            for os, osdata in insightdata.get('specific_operating_systems').items():
                related_section = Section.objects.get(
                    title=osdata.get('section'))

                OperatingSystemSpecificSection.objects.get_or_create(
                    section=related_section,
                    operating_system=os, defaults={'text': osdata.get('text')})

        self.LOGS.append(log.log('Added/updated insights: ' +
                ', '.join([x.get("title") for x in data])))

        self.SAVE_DIR = self.SAVE_DIR = f'{LogSaver.LOG_DIR}/ingestinsights'
        if self._save(data='ingestinsights', name='warnings.md', warnings=True) or self._save(data='ingestinsights', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' + self.SAVE_DIR, force=True)
