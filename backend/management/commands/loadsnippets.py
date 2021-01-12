from django.core.management import BaseCommand
from backend.dhri.log import Logger
from backend.dhri_settings import AUTO_SNIPPETS
from backend.models import Snippet


log = Logger(name='loadsnippets')


def create_snippets(AUTO_SNIPPETS=AUTO_SNIPPETS):
    for identifier, snippet in list(AUTO_SNIPPETS.items()):
        if not snippet:
            log.warning(f'Snippet `{identifier}` has no text and will not be loaded...')
            continue
        
        obj, created = Snippet.objects.get_or_create(
            identifier=identifier,
            snippet=snippet
        )
        log.created(created, 'Snippet', obj.identifier, obj.id)



class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Create default snippets'

    def handle(self, *args, **options):
        if len(AUTO_SNIPPETS):
            create_snippets(AUTO_SNIPPETS)
        else:
            log.warning(
                'No auto snippet information set up. Will skip automatic import of snippets.')
