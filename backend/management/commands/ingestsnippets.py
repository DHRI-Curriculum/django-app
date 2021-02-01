from website.models import Snippet
from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger, Input
from backend.dhri_settings import AUTO_SNIPPETS
from ._shared import get_name


# TODO #362: Note that there is no buildsnippets since it comes in straight from a YAML file defined in dhri_settings

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with snippet information into the database'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(name=get_name(__file__), force_verbose=options.get('verbose'), force_silent=options.get('silent'))
        input = Input(name=get_name(__file__))
        data = AUTO_SNIPPETS

        for identifier, snippetdata in data.items():
            snippet, created = Snippet.objects.get_or_create(identifier=identifier)
            
            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Snippet `{identifier}` already exists. Update with new definition? [y/N]')
                if choice.lower() != 'y':
                    continue
            
            Snippet.objects.filter(identifier=identifier).update(
                snippet=snippetdata
            )

        log.log('Added/updated snippets: ' + ', '.join([x for x in data]))
