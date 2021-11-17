from website.models import Snippet
from django.core.management import BaseCommand
from backend.logger import Logger, Input
from backend.settings import AUTO_SNIPPETS
from backend.markdown_parser import PARSER



# TODO #362: Note that there is no buildsnippets since it comes in straight from a YAML file defined in dhri_settings

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with snippet information into the database'
    requires_migrations_checks = True
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true')
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

            if not created and not options.get('force'):
                choice = input.ask(
                    f'Snippet `{identifier}` already exists. Update with new definition? [y/N]')
                if choice.lower() != 'y':
                    continue

            Snippet.objects.filter(identifier=identifier).update(
                snippet=PARSER.convert(snippetdata)
            )

        log.log('Added/updated snippets: ' +
                                 ', '.join([x for x in data]))

        if log._save(data='ingestsnippets', name='warnings.md', warnings=True) or log._save(data='ingestsnippets', name='logs.md', warnings=False, logs=True) or log._save(data='ingestsnippets', name='info.md', warnings=False, logs=False, info=True):
            log.log(f'Log files with any warnings and logging information is now available in: `{log.LOG_DIR}`', force=True)