from django.core.management import BaseCommand
from django.contrib.auth.models import User, Group
from backend.dhri_settings import AUTO_USERS
from backend.dhri.log import Logger
from django.core.management import execute_from_command_line
from django.conf import settings


log = Logger(name='localserver')

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Runserver on localhost'

    def handle(self, *args, **options):
        if not '*' in settings.ALLOWED_HOSTS:
            log.warning('Adding \'*\' to ALLOWED_HOSTS. You might want to change ALLOWED_HOSTS in app.settings to include \'*\'.')
            settings.ALLOWED_HOSTS.append('*')
        args = ['name', 'runserver', '0.0.0.0:80']
        execute_from_command_line(args)