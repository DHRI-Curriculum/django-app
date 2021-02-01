from django.core.management import BaseCommand, call_command

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Shortcut to run through all the build commands in the correct order'

    def add_arguments(self, parser):
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--force_download', action='store_true')

    def handle(self, *args, **options):
        call_command('buildgroups', silent=options.get('silent'), verbose=options.get('verbose'))
        call_command('buildusers', silent=options.get('silent'), verbose=options.get('verbose'))
        call_command('buildglossary', silent=options.get('silent'), verbose=options.get('verbose'), force_download=options.get('force_download'))
        call_command('buildinstalls', silent=options.get('silent'), verbose=options.get('verbose'), force_download=options.get('force_download'))
        call_command('buildinsights', silent=options.get('silent'), verbose=options.get('verbose'), force_download=options.get('force_download'))
        call_command('buildworkshop', '--force', all=True, silent=options.get('silent'), verbose=options.get('verbose'), force_download=options.get('force_download'))
        call_command('buildblurbs', silent=options.get('silent'), verbose=options.get('verbose'))