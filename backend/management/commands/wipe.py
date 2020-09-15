from django.core.management import BaseCommand
from django.contrib.auth.models import User, Group
from backend.models import ALL_MODELS
from backend.dhri.log import Logger
from .loadglossary import wipe_terms
from .loadinsights import wipe_insights


log = Logger(name='wipe')


def wipe():
    log.log("General wipe activated.", force=True) #  The script will proceed in VERBOSE mode automatically?
    for model in ALL_MODELS:
        model.objects.all().delete()
        log.log(f'All {model._meta.verbose_name_plural} removed.', force=True) #  The script will proceed in VERBOSE mode automatically?


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Wipe the database from DHRI Curriculum content'

    def handle(self, *args, **options):
        wipe()
        wipe_terms()
        wipe_insights()