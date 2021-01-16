from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger
from .imports import *
from backend import dhri_settings
from backend.dhri.loader import GlossaryLoader
import yaml
import pathlib
import shutil

log = Logger(name='build-users')
SAVE_DIR = f'{settings.BASE_DIR}/_preload/_meta/users'
SAVE_DIR_IMG = f'{settings.BASE_DIR}/_preload/_meta/users/images'
DATA_FILE = 'users.yml'


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from user information (provided through dhri_settings.AUTO_USER)'

    def handle(self, *args, **options):
        users = list()

        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        if not pathlib.Path(SAVE_DIR_IMG).exists():
            pathlib.Path(SAVE_DIR_IMG).mkdir(parents=True)

        for cat in list(dhri_settings.AUTO_USERS.keys()):
            for u in dhri_settings.AUTO_USERS[cat]:
                is_staff = cat == 'STAFF'
                is_super = cat == 'SUPER'

                user = {
                    'username': u.get('username'),
                    'password': u.get('password', ''),
                    'first_name': u.get('first_name', ''),
                    'last_name': u.get('last_name', ''),
                    'email': u.get('email', ''),
                    'profile': {
                        'image': '',
                        'bio': u.get('bio'),
                        'pronouns': u.get('pronouns'),
                        'links': []
                    },
                    'superuser': False,
                    'staff': False,
                    'groups': u.get('groups', [])
                }
                if is_super:
                    user['superuser'] = True
                elif is_staff:
                    user['staff'] = True

                if u.get('img'):
                    filename = u['img'].split('/')[-1]
                    user['profile']['image'] = f'{SAVE_DIR_IMG}/{filename}'
                    shutil.copy(u['img'], user['profile']['image'])

                for link in u.get('links', []):
                    user['profile']['links'].append({
                        'label': link.get('text'),
                        'url': link.get('url'),
                        'cat': link.get('cat')
                    })

                users.append(user)

        # Save all data
        with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
            file.write(yaml.dump(users))
