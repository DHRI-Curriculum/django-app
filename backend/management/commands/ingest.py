from django.core.management import BaseCommand, call_command

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Shortcut to run through all the ingest commands in the correct order'

    def handle(self, *args, **options):
        call_command('ingestgroups', '--forceupdate')
        call_command('ingestusers', '--forceupdate')
        call_command('ingestglossary', '--forceupdate')
        call_command('ingestinstalls', '--forceupdate')
        call_command('ingestinsights', '--forceupdate')
        call_command('ingestworkshop', '--forceupdate') #TODO #326             # call_command('ingestblurbs', '--forceupdate') #TODO #326 (consolidate into `ingestrepo`)
        call_command('ingestsnippets', '--forceupdate') #TODO #326