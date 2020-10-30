from django.core.management import BaseCommand
from backend.dhri.log import Logger
from django.core.management import execute_from_command_line
from django.conf import settings


log = Logger(name='localserver')


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Re-save every model'

    def handle(self, *args, **options):
        from backend.models import ALL_MODELS
        for model in ALL_MODELS:
            for obj in model.objects.all():
                obj.save()
                print(obj, 'saved.')
