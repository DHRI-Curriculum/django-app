from django.core.management import BaseCommand
from django.contrib.auth.models import User, Group
from backend.models import ALL_MODELS
from backend.dhri.log import Logger


log = Logger(name='wipe')


def wipe():
    log.log("Wipe activated.", force=True) #  The script will proceed in VERBOSE mode automatically?
    for model in ALL_MODELS:
        model.objects.all().delete()
        log.log(f' {model.__str__} removed.', force=True) #  The script will proceed in VERBOSE mode automatically?


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Wipe the database from DHRI Curriculum content'

    def handle(self, *args, **options):
        wipe()