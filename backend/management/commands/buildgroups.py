from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger
from backend import dhri_settings
import yaml
import pathlib

log = Logger(name='build-groups')
SAVE_DIR = f'{settings.BASE_DIR}/_preload/_meta/users'
DATA_FILE = 'groups.yml'


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from groups information (provided through dhri_settings.AUTO_GROUPS)'

    def handle(self, *args, **options):
        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        permissions = {}

        for group_name in dhri_settings.AUTO_GROUPS:
            permissions[group_name] = list()
            for model_cls in dhri_settings.AUTO_GROUPS[group_name]:
                for perm_name in dhri_settings.AUTO_GROUPS[group_name][model_cls]:
                    # Generate permission name as Django would generate it
                    codename = perm_name + '_' + model_cls._meta.model_name
                    permissions[group_name].append(codename)

        # Save all data
        with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
            file.write(yaml.dump(permissions))
