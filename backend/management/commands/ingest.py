from django.contrib.auth.models import User
from django.core.management import BaseCommand, call_command
from ._shared import all_models
from backend.logger import get_or_default, Logger


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Shortcut to run through all the ingest commands in the correct order and with the --forceupdate flag automatically turned on'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true',
                            help='Removes all the DHRI-related objects in the database and starts a fresh installation.')
        parser.add_argument('--resetusers', action='store_true',
                            help='Removes all the users in the database and starts a fresh installation from the users.yml file.')
        parser.add_argument('--force', action='store_true',
                            help='Automatically approves any requests to replace/update existing data in the database.')
        parser.add_argument('--silent', action='store_true',
                            help='Makes as little output as possible, although still saves all the information in log files (see debugging docs).')
        parser.add_argument('--verbose', action='store_true',
                            help='Provides all output possible, which can be overwhelming. Good for debug purposes, not for the faint of heart.')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
            force_verbose=options.get('verbose'),
            force_silent=options.get('silent')
        )

        if options.get('reset'):
            if options.get('force'):
                i = get_or_default(
                    f'Warning: This script is about to remove ALL OF THE OBJECTS from the database. Are you sure you want to continue?', color='red', default_variable='N')
                if i.lower() != 'y':
                    log.error('User opted to stop.')
            for model in all_models:
                name = model.__name__.replace('_', ' ')
                if not options.get('force'):
                    i = get_or_default(
                        f'Warning: This will remove all the `{name}` objects. Are you sure you want to continue?', color='red', default_variable='N')
                    if i.lower() != 'y':
                        continue
                model.objects.all().delete()

                log.log(f'Removed all `{name}` objects.')
            
        if options.get('resetusers'):
            if options.get('force'):
                i = get_or_default(
                    f'Warning: This script is about to remove ALL OF THE USERS from the database. Are you sure you want to continue?', color='red', default_variable='N')
                if i.lower() != 'y':
                    log.error('User opted to stop.')
            
            User.objects.all().delete()

            log.log(f'Removed all users.')

        call_command('ingestgroups',
                     forceupdate=True,
                     silent=options.get('silent'),
                     verbose=options.get('verbose'))
        call_command('ingestusers',
                     forceupdate=True,
                     silent=options.get('silent'),
                     verbose=options.get('verbose'))
        call_command('ingestglossary',
                     forceupdate=True,
                     silent=options.get('silent'),
                     verbose=options.get('verbose'))
        call_command('ingestinstalls',
                     forceupdate=True,
                     silent=options.get('silent'),
                     verbose=options.get('verbose'))
        call_command('ingestinsights',
                     forceupdate=True,
                     silent=options.get('silent'),
                     verbose=options.get('verbose'))
        call_command('ingestworkshop',
                     forceupdate=True,
                     silent=options.get('silent'),
                     verbose=options.get('verbose'),
                     no_reminder=True)
        call_command('ingestsnippets',
                     forceupdate=True,
                     silent=options.get('silent'),
                     verbose=options.get('verbose'))
        call_command('ingestblurbs',
                     forceupdate=True,
                     silent=options.get('silent'),
                     verbose=options.get('verbose'))
        call_command('ingestprerequisites',
                     forceupdate=True,
                     silent=options.get('silent'),
                     verbose=options.get('verbose'))
