from django.core.management import BaseCommand
from backend.dhri.log import Logger, log_created
from backend.models import Page


log = Logger(name='loadinstalls')


def create_installations():
    print('create installations...')
    pass


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Load all installs'

    def handle(self, *args, **options):
        create_installations()