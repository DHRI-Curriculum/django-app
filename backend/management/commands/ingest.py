from django.core.management import BaseCommand, call_command

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Shortcut to run through all the ingest commands in the correct order'

    def handle(self, *args, **options):
        call_command('ingestgroups', '--forceupdate')
        call_command('ingestusers', '--forceupdate')
        call_command('ingestglossary', '--forceupdate')
        call_command('ingestinstalls')
        call_command('ingestinsights')
        call_command('ingestrepo', '--reset') #TODO: Make this force its way through (overriding existing folders.)
        call_command('ingestblurbs')