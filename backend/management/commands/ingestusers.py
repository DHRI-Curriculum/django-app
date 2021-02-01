from django.contrib.auth.models import User
from learner.models import Profile
from django.core.management import BaseCommand
from django.core.files import File
from django.conf import settings
from backend.dhri.log import Logger, Input
from ._shared import test_for_required_files, get_yaml, get_name

import yaml
import pathlib
import os

log = Logger(name=get_name(__file__))
input = Input(name=get_name(__file__))
SAVE_DIR = f'{settings.BASE_DIR}/_preload/_meta/users'
FULL_PATH = f'{SAVE_DIR}/users.yml'
REQUIRED_PATHS = [
    (SAVE_DIR, f'The required directory ({SAVE_DIR}) does not exist. Did you run `python manage.py buildusers` before you ran this command?'),
    (FULL_PATH, f'The required data file ({FULL_PATH}) does not exist. Did you run `python manage.py buildusers` before you ran this command?')
]


def get_profile_picture_path(image_file, relative_to_upload_field=False):
    if not relative_to_upload_field:
        return settings.MEDIA_ROOT + '/' + Profile.image.field.upload_to + '/' + os.path.basename(image_file)
    
    return Profile.image.field.upload_to + '/' + os.path.basename(image_file)


def profile_picture_exists(image_file):
    return os.path.exists(get_profile_picture_path(image_file))


def get_default_profile_picture():
    return Profile.image.field.upload_to + '/' + Profile.image.field.default


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with user information into the database'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')

    def handle(self, *args, **options):
        test_for_required_files(REQUIRED_PATHS=REQUIRED_PATHS, log=log)
        data = get_yaml(f'{FULL_PATH}')

        for userdata in data:
            if not userdata.get('username'):
                log.error(f'Username is required. Check the datafile ({FULL_PATH}) to make sure that all the users in the file are assigned a username.')

            user, created = User.objects.get_or_create(username=userdata.get('username'))

            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'User `{userdata.get("username")}` already exists. Update with new information? [y/N]')
                if choice.lower() != 'y':
                    continue
            
            User.objects.filter(username=userdata.get('username')).update(
                first_name = userdata.get('first_name'),
                last_name = userdata.get('last_name'),
                email = userdata.get('email'),
                password = userdata.get('password'),
                is_superuser = userdata.get('superuser'),
                is_staff = userdata.get('staff'),
            )

            if not userdata.get('profile'):
                log.error(f'User {userdata.get("username")} does not have profile information (bio, image, links, and/or pronouns) added. Make sure you add all this information for each user in the datafile before running this command ({FULL_PATH}).')

            profile, created = Profile.objects.get_or_create(user=user)

            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'User `{userdata.get("username")}` already has a profile. Update with new information? [y/N]')
                if choice.lower() != 'y':
                    continue

            Profile.objects.filter(user=user).update(
                bio = userdata.get('profile', {}).get('bio'),
                pronouns = userdata.get('profile', {}).get('pronouns'),
            )

            profile.refresh_from_db()

            if userdata.get('profile', {}).get('image'):
                if profile_picture_exists(userdata.get('profile', {}).get('image')):
                    profile.image.name = get_profile_picture_path(userdata.get('profile', {}).get('image'), True)
                    profile.save()
                else:
                    with open(userdata.get('profile', {}).get('image'), 'rb') as f:
                        profile.image = File(f, name=os.path.basename(f.name))
                        profile.save()
            else:
                profile.image.name = get_default_profile_picture()
                profile.save()
                log.warning(f'User {userdata.get("username")} does not have an image assigned to them. Add filepaths to an existing file in your datafile ({FULL_PATH}) if you want to update the specific user.')

        log.log('Added/updated users: ' + ', '.join([x.get('username') for x in data]))
