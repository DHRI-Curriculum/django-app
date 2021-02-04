from workshop.models import Blurb, Workshop
from django.core.management import BaseCommand
from django.contrib.auth.models import User
from backend.dhri.log import Logger, Input
from backend.mixins import convert_html_quotes
from ._shared import get_yaml, get_name, get_all_existing_workshops, LogSaver


class Command(LogSaver, BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with blurb information into the database'
    requires_migrations_checks = True
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')
        parser.add_argument('--name', nargs='+', type=str)
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(name=get_name(__file__), force_verbose=options.get('verbose'), force_silent=options.get('silent'))
        input = Input(name=get_name(__file__))
        
        workshops = get_all_existing_workshops()
        
        if options.get('name'):
            workshops = get_all_existing_workshops(options.get('name'))

        for _ in workshops:
            name, path = _
            DATAFILE = f'{path}/blurb.yml'
            
            data = get_yaml(DATAFILE)

            if not data.get('user'):
                log.error(f'Username was not defined for the blurb for workshop {name} was not found. Check the datafile {DATAFILE} to verify the username attributed to the blurb.')

            if not data.get('workshop'):
                self.WARNINGS.append(log.warning(f'Blurb had no workshop assigned, but will proceed with the blurb\'s parent folder ({name}) as assumed workshop. To fix this warning, you can try running python manage.py buildblurbs before running ingestblurbs.'))
                data['workshop'] = name
            
            if not data.get('text'):
                log.error(f'Blurb has no text assigned, and thus could not be ingested. Check the datafile {DATAFILE} to verify the workshop attributed to the blurb.')

            try:
                user = User.objects.get(username=data.get('user'))
            except:
                log.error(f'The user attributed to the blurb ({data.get("username")}) was not found in the database. Did you try running python manage.py ingestusers before running ingestblurbs?')

            try:
                workshop = Workshop.objects.get(slug=data.get('workshop'))
            except:
                log.error(f'The blurb\'s attached workshop ({data.get("workshop")}) was not found in the database. Did you try running python manage.py ingestworkshop --name {data.get("workshop")} before running ingestblurbs?')

            blurb, created = Blurb.objects.get_or_create(user=user, workshop=workshop, defaults={'text': convert_html_quotes(data.get('text'))})
            
            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Frontmatter for workshop `{workshop}` already exists. Update with new content? [y/N]')
                if choice.lower() != 'y':
                    continue
            
            blurb.text = data.get('text')
            blurb.save()

        self.LOGS.append(log.log('Added/updated blurbs for workshops: ' + ', '.join([x[0] for x in workshops])))

        self.SAVE_DIR = self.SAVE_DIR = f'{LogSaver.LOG_DIR}/ingestblurbs'
        if self._save(data='ingestblurbs', name='warnings.md', warnings=True) or self._save(data='ingestblurbs', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' + self.SAVE_DIR, force=True)