from website.models import Snippet
from django.core.management import BaseCommand
from backend.dhri.log import Logger, Input
from backend.dhri_settings import AUTO_SNIPPETS
from backend.dhri.markdown_parser import PARSER
from ._shared import LogSaver


# TODO #362: Note that there is no buildsnippets since it comes in straight from a YAML file defined in dhri_settings

class Command(LogSaver, BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with snippet information into the database'
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

        data = AUTO_SNIPPETS

        for identifier, snippetdata in data.items():
            snippet, created = Snippet.objects.get_or_create(
                identifier=identifier)

            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Snippet `{identifier}` already exists. Update with new definition? [y/N]')
                if choice.lower() != 'y':
                    continue

            Snippet.objects.filter(identifier=identifier).update(
                snippet=PARSER.convert(snippetdata)
            )

        self.LOGS.append(log.log('Added/updated snippets: ' +
                                 ', '.join([x for x in data])))

        self.SAVE_DIR = self.SAVE_DIR = f'{LogSaver.LOG_DIR}/ingestsnippets'
        if self._save(data='ingestsnippets', name='warnings.md', warnings=True) or self._save(data='ingestsnippets', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' +
                    self.SAVE_DIR, force=True)
