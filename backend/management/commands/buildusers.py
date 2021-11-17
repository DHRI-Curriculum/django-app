from backend.markdown_parser import PARSER
from django.core.management import BaseCommand
from backend.logger import Logger
from backend import settings
from shutil import copyfile
from ._shared_functions import crop_and_save

import yaml
import pathlib
import requests

SAVE_DIR = f'{settings.BUILD_DIR}_meta/users'
SAVE_DIR_IMG = f'{SAVE_DIR}/images'
DATA_FILE = 'users.yml'

MAX_SIZE = 400



class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from user information (provided through backend.settings.AUTO_USER)'
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--nocrop', action='store_true')
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
                     force_verbose=options.get('verbose'),
                     force_silent=options.get('silent')
                     )

        log.log('Building user files... Please be patient as this can take some time.')

        users = list()

        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        if not pathlib.Path(SAVE_DIR_IMG).exists():
            pathlib.Path(SAVE_DIR_IMG).mkdir(parents=True)

        all_categories = list(settings.AUTO_USERS.keys())

        for cat in all_categories:

            all_users = settings.AUTO_USERS[cat]
            
            log.BAR(all_users, max_value=len(all_users))

            for i, u in enumerate(all_users):
                log.BAR.update(i)
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
                        'bio': '',
                        'pronouns': u.get('pronouns'),
                        'links': []
                    },
                    'superuser': is_super,
                    'staff': is_staff,
                    'groups': u.get('groups', [])
                }

                for link in u.get('links', []):
                    user['profile']['links'].append({
                        'label': link.get('text'),
                        'url': link.get('url'),
                        'cat': link.get('cat')
                    })

                if u.get('bio'):
                    user['profile']['bio'] = PARSER.fix_html(u.get('bio'))

                if u.get('img'):
                    if options.get('nocrop'):
                        filename = u['img'].split('/')[-1]
                        user['profile']['image'] = f'{SAVE_DIR_IMG}/{filename}'
                        copyfile(u['img'], user['profile']['image'])
                    else:
                        filename = u['img'].split('/')[-1].split('.')[0]
                        user['profile']['image'] = f'{SAVE_DIR_IMG}/{filename}.jpg'
                        crop_and_save(u['img'], user['profile']['image'], MAX_SIZE)
                else:
                    # Ask user if they want to get image from GitHub instead? (force: auto-try)

                    # Then, try to get image from GitHub.
                    fixed = False
                    if len([x for x in user['profile']['links'] if 'github.com/' in x['url']]):
                        url = [x for x in user['profile']['links'] if 'github.com/' in x['url']][0]['url']
                        gh_username = [x for x in url.split('/') if x][2]
                        
                        r = requests.get(f'https://www.github.com/{gh_username}.png')
                        if r.status_code == 200:
                            user['profile']['image'] = f'{SAVE_DIR_IMG}/{gh_username}.png'
                            with open(user['profile']['image'], 'wb+') as f:
                                f.write(r.content)
                            fixed = True
                            
                    if not fixed:
                        log.warning(f'User `{u.get("username")}` does not have an image assigned to them and will be assigned the default picture. Add filepaths to an existing file in your datafile (`{SAVE_DIR}/{DATA_FILE}`) or follow the steps in the documentation to add user images if you want to make sure the specific user has a profile picture. Then, rerun `python manage.py buildusers` or `python manage.py build`')

                users.append(user)

            log.BAR.finish()

        # Save all data
        with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
            file.write(
                yaml.dump({'users': users, 'default': settings.AUTO_USER_DEFAULT}))

        log.log(f'Saved user datafile: {SAVE_DIR}/{DATA_FILE}.')

        if log._save(data='buildusers', name='warnings.md', warnings=True) or log._save(data='buildusers', name='logs.md', warnings=False, logs=True) or log._save(data='buildusers', name='info.md', warnings=False, logs=False, info=True):
            log.log(f'Log files with any warnings and logging information is now available in: `{log.LOG_DIR}`', force=True)