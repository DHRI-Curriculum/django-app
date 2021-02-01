from django.core.management import BaseCommand, call_command

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Shortcut to run through all the ingest commands in the correct order and with the --forceupdate flag automatically turned on'

    def add_arguments(self, parser):
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        call_command('ingestgroups', '--forceupdate', silent=options.get('silent'), verbose=options.get('verbose'))
        call_command('ingestusers', '--forceupdate', silent=options.get('silent'), verbose=options.get('verbose'))
        call_command('ingestglossary', '--forceupdate', silent=options.get('silent'), verbose=options.get('verbose'))
        call_command('ingestinstalls', '--forceupdate', silent=options.get('silent'), verbose=options.get('verbose'))
        call_command('ingestinsights', '--forceupdate', silent=options.get('silent'), verbose=options.get('verbose'))
        call_command('ingestworkshop', '--forceupdate', silent=options.get('silent'), verbose=options.get('verbose'))
        call_command('ingestsnippets', '--forceupdate', silent=options.get('silent'), verbose=options.get('verbose'))
        call_command('ingestblurbs', '--forceupdate', silent=options.get('silent'), verbose=options.get('verbose'))