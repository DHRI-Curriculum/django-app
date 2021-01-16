from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger
from backend.dhri.insight_parser import InsightLoader
import yaml
import pathlib

log = Logger(name='build-insights')
SAVE_DIR = f'{settings.BASE_DIR}/_preload/_insights'
DATA_FILE = 'insights.yml'


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from insight repository (provided through --repo parameter)'

    def handle(self, *args, **options):
        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        loader = InsightLoader()
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
