from django.core.management import BaseCommand
from django.contrib.auth.models import User, Group
from backend.dhri_settings import AUTO_USERS, USER_SETUP
from backend.dhri.log import Logger
from django.core.files import File


log = Logger(name='loadusers')


def create_users(AUTO_USERS=AUTO_USERS):
    for cat in list(AUTO_USERS.keys()):
        print(cat)
        for u in AUTO_USERS[cat]:
            is_staff = cat == 'STAFF'
            is_super = cat == 'SUPER'
            is_user = cat == 'USER'

            # print(is_staff, is_super, is_user)

            username = u.get('username')

            # TODO: Set all force to False
            if User.objects.filter(username=username).count():
                log.log(f"Deleting existing user `{username}`...", force=True)
                User.objects.filter(username=username).delete()

            if is_super:
                user = User.objects.create_superuser(
                    username=username,
                    password = u.get('password'),
                    first_name = u.get('first_name'),
                    last_name = u.get('last_name')
                )
                log.log(f'Superuser `{user}` added.', force=True)
            else:
                user = User.objects.create_user(
                    password = u.get('password'),
                    username=username,
                    first_name = u.get('first_name'),
                    last_name = u.get('last_name')
                )
                if is_staff:
                    user.is_staff=True
                    user.save()
                    log.log(f'Staff user `{user}` added.', force=True)
                else:
                    log.log(f'User `{user}` added.', force=True)

            # Profile
            if u.get('bio') or u.get('img'):
                if u.get('bio'):
                    user.profile.bio = u.get('bio')
                if u.get('img'):
                    try:
                        import os
                        with open(u.get('img'), 'rb') as f:
                            user.profile.image = File(f, name=os.path.basename(f.name))
                            user.profile.save()
                    except FileNotFoundError:
                        print(f'Could not find image for user with username `{u.get("username")}`: Make sure the file exists: `{u.get("img")}` in the root directory of the app.')
                        exit()
                user.save()
                log.log(f'`{user.profile}` saved with bio information and photo.', force=True)

            # Groups
            for group in u.get('groups', []):
                try:
                    if Group.objects.get(name=group):
                        Group.objects.get(name=group).user_set.add(user)
                        log.log(f'{user} --> added to `{group}`.')
                except:
                    log.error(f'Error: Could not add {user} to group {group}.')
                    log.error(f'If you are certain that the group should exist, try running `manage.py create_groups` first.')

            '''
            print()
            print()
            print(u.get('blurb', {'text': None, 'workshop': None}).get('text'))
            print(u.get('blurb', {'text': None, 'workshop': None}).get('workshop'))
            for group in u.get('groups', []):
                print(group)
            '''
    exit()

    for cat in AUTO_USERS:
        for username, settings in AUTO_USERS[cat].items():
            groups = settings.pop('groups')
            for group in groups:
                try:
                    if Group.objects.get(name=group):
                        Group.objects.get(name=group).user_set.add(u)
                        log.log(f'--> added to `{group}`.')
                except:
                    log.error(f'Error: Could not add {u} to group {group}.')
                    log.error(f'If you are certain that the group should exist, try running `manage.py create_groups` first.')


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Create default users'

    def handle(self, *args, **options):
        create_users(AUTO_USERS)