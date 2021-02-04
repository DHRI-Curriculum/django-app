from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Shortcut to run through all the build commands in the correct order'

    def add_arguments(self, parser):
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--forcedownload', action='store_true')

    def handle(self, *args, **options):
        call_command('buildgroups',
                     silent=options.get('silent'),
                     verbose=options.get('verbose'))
        call_command('buildusers',
                     silent=options.get('silent'),
                     verbose=options.get('verbose'))
        call_command('buildglossary',
                     silent=options.get('silent'),
                     verbose=options.get('verbose'),
                     forcedownload=options.get('forcedownload'))
        call_command('buildinstalls',
                     silent=options.get('silent'), verbose=options.get('verbose'),
                     forcedownload=options.get('forcedownload'))
        call_command('buildinsights',
                     silent=options.get('silent'),
                     verbose=options.get('verbose'),
                     forcedownload=options.get('forcedownload'))
        call_command('buildworkshop',
                     silent=options.get('silent'),
                     verbose=options.get('verbose'),
                     forcedownload=options.get('forcedownload'),
                     force=True,
                     all=True)
        call_command('buildblurbs',
                     silent=options.get('silent'),
                     verbose=options.get('verbose'))
