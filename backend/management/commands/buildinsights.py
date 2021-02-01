from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger
from backend.dhri.insight_parser import InsightLoader
from ._shared import get_name
import yaml
import pathlib

SAVE_DIR = f'{settings.BASE_DIR}/_preload/_insights'
DATA_FILE = 'insights.yml'


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from insight repository'

    def add_arguments(self, parser):
        parser.add_argument('--force_download', action='store_true')
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(name=get_name(__file__), force_verbose=options.get('verbose'), force_silent=options.get('silent'))

        log.log('Building insight files...')

        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        loader = InsightLoader(force_download=options.get('force_download'))
        insights = list()

        for _, i in loader.insights.items():
            insight = {
                'title': i.header.strip(),
                'text': i.introduction.strip(),
                'sections': [],
                'specific_operating_systems': {}
            }

            order = 1
            for section, text in i.sections.items():
                insight['sections'].append({
                    'title': section.strip(),
                    'text': text.strip(),
                    'order': order,
                })
                order += 1

            for operating_system, d in i.os_specific.items():
                insight['specific_operating_systems'][operating_system] = d

            insights.append(insight)

        # Save all data
        with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
            file.write(yaml.dump(insights))

        log.log(f'Saved insights data file: {SAVE_DIR}/{DATA_FILE}')