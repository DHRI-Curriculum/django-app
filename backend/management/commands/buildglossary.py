from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger
from backend import dhri_settings
from backend.dhri.loader import GlossaryLoader
from ._shared import LogSaver
import yaml
import pathlib

SAVE_DIR = f'{settings.BASE_DIR}/_preload/_meta/glossary'
DATA_FILE = 'glossary.yml'


class Command(LogSaver, BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from glossary repository (provided through dhri_settings.GLOSSARY_REPO)'
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

        loader = GlossaryLoader(
            dhri_settings.GLOSSARY_REPO, force_download=options.get('forcedownload'))

        glossary = list()

        for term in loader.all_terms:
            glossary.append({
                'term': loader.terms[term].term.strip(),
                'explication': loader.terms[term].explication.strip()
            })

        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
            file.write(yaml.dump(glossary))

        self.LOGS.append(
            log.log(f'Saved glossary datafile: {SAVE_DIR}/{DATA_FILE}.'))

        self.SAVE_DIR = self.SAVE_DIR = f'{LogSaver.LOG_DIR}/buildglossary'
        if self._save(data='buildglossary', name='warnings.md', warnings=True) or self._save(data='buildglossary', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' +
                    self.SAVE_DIR, force=True)
