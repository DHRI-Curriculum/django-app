from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger
from backend import dhri_settings
from shutil import copyfile
from PIL import Image
from ._shared import LogSaver
import yaml
import pathlib

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


class Command(LogSaver, BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from user information (provided through dhri_settings.AUTO_USER)'
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--nocrop', action='store_true')
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__, force_verbose=options.get('verbose'), force_silent=options.get('silent'))

        log.log('Building user files... Please be patient as this can take some time.')

        users = list()

        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        if not pathlib.Path(SAVE_DIR_IMG).exists():
            pathlib.Path(SAVE_DIR_IMG).mkdir(parents=True)

        for cat in list(dhri_settings.AUTO_USERS.keys()):
            for u in dhri_settings.AUTO_USERS[cat]:
                is_staff = cat == 'STAFF'
                is_super = cat == 'SUPER'

                if is_super:
                    is_staff = True

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
                else:
                    self.WARNINGS.append(log.warning(f'User `{u.get("username")}` does not have an image assigned to them. Add filepaths to an existing file in your datafile (`{SAVE_DIR}/{DATA_FILE}`) or follow the steps in the documentation to add user images if you want to make sure the specific user has a profile picture. Then, rerun `python manage.py buildusers` or `python manage.py build`'))

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

        self.LOGS.append(log.log(f'Saved user datafile: {SAVE_DIR}/{DATA_FILE}.'))
            
        self.SAVE_DIR = self.SAVE_DIR = f'{LogSaver.LOG_DIR}/buildusers'
        if self._save(data='buildusers', name='warnings.md', warnings=True) or self._save(data='buildusers', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' + self.SAVE_DIR, force=True)
