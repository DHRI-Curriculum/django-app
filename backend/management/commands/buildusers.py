from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger
from backend import dhri_settings
from backend.dhri.loader import GlossaryLoader

from shutil import copyfile
from PIL import Image

import yaml
import pathlib

log = Logger(name='build-users')
SAVE_DIR = f'{settings.BASE_DIR}/_preload/_meta/users'
SAVE_DIR_IMG = f'{settings.BASE_DIR}/_preload/_meta/users/images'
DATA_FILE = 'users.yml'

MAX_SIZE = 400

def crop_center(pil_img, crop_width, crop_height):
    # https://note.nkmk.me/en/python-pillow-square-circle-thumbnail/
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from user information (provided through dhri_settings.AUTO_USER)'

    def add_arguments(self, parser):
        parser.add_argument('--nocrop', action='store_true')
    
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
                    if options.get('nocrop'):
                        filename = u['img'].split('/')[-1]
                        user['profile']['image'] = f'{SAVE_DIR_IMG}/{filename}'
                        copyfile(u['img'], user['profile']['image'])
                    else:
                        filename = u['img'].split('/')[-1].split('.')[0]
                        user['profile']['image'] = f'{SAVE_DIR_IMG}/{filename}.jpg'
                        with open(u['img'], 'rb') as f:
                            cropped_img = Image.open(f)
                            w, h = cropped_img.size
                            if w != h:
                                cropped_img = crop_center(cropped_img, min(cropped_img.size), min(cropped_img.size)) # crop to square from center!
                            cropped_img = cropped_img.resize((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
                            cropped_img.save(user['profile']['image'], 'jpeg', quality=50)

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
