from django.core.management import BaseCommand
from backend.settings import BUILD_DIR, INSIGHT_REPO
from backend.logger import Logger
from backend.github import InsightCache
import yaml
import pathlib

SAVE_DIR = f'{BUILD_DIR}_insights'
DATA_FILE = 'insights.yml'


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from insight repository'
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
                     force_verbose=options.get('verbose'),
                     force_silent=options.get('silent')
                     )

        log.log(
            'Building insight files... Please be patient as this can take some time.')

        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        loader = InsightCache(repository=INSIGHT_REPO[0], branch=INSIGHT_REPO[1], log=log)
        insights = list()

        for insight_data in loader.data:
            insights.append(insight_data)

        # Save all data
        with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
            file.write(yaml.dump(insights))

        log.log(f'Saved insights data file: {SAVE_DIR}/{DATA_FILE}')

        if log._save(data='buildinsights', name='warnings.md', warnings=True) or log._save(data='buildinsights', name='logs.md', warnings=False, logs=True) or log._save(data='buildinsights', name='info.md', warnings=False, logs=False, info=True):
            log.log(f'Log files with any warnings and logging information is now available in: `{log.LOG_DIR}`', force=True)