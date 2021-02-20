from django.core.management import BaseCommand
from backend.logger import Logger
from backend import settings
from backend.github import GlossaryCache

import yaml
import pathlib

SAVE_DIR = f'{settings.BUILD_DIR}_meta/glossary'
DATA_FILE = 'glossary.yml'


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from glossary repository (provided through backend.settings.GLOSSARY_REPO)'
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--forcedownload', action='store_true')
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
            force_verbose=options.get('verbose'),
            force_silent=options.get('silent')
        )
        log.log('Building glossary... Please be patient as this can take some time.')

        loader = GlossaryCache(repository='glossary', branch='v2.0', log=log) # TODO: import from settings here

        glossary = list()

        for term_data in loader.data:
            glossary.append({
                'term': term_data['term'],
                'explication': term_data['explication'],
                'readings': term_data['readings'],
                'tutorials': term_data['tutorials'],
                'cheat_sheets': term_data['cheat_sheets'],
            })

        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
            file.write(yaml.dump(glossary))

        log.log(f'Saved glossary datafile: {SAVE_DIR}/{DATA_FILE}.')

        if log._save(data='buildglossary', name='warnings.md', warnings=True) or log._save(data='buildglossary', name='logs.md', warnings=False, logs=True) or log._save(data='buildglossary', name='info.md', warnings=False, logs=False, info=True):
            log.log(f'Log files with any warnings and logging information is now available in: `{log.LOG_DIR}`', force=True)