from django.core.management import BaseCommand
from django.contrib.auth.models import User, Group
from backend.dhri_settings import USERS
from backend.dhri.log import Logger


log = Logger(name='loadusers')


def create_users(USERS=USERS):
    for cat in USERS:
        for username, settings in USERS[cat].items():
            groups = settings.pop('groups')
            if User.objects.filter(username=username).count(): User.objects.filter(username=username).delete()
            if cat == 'SUPER':
                u = User.objects.create_superuser(username=username, **settings)
                log.log(f'Superuser `{u}` added.')

            else:
                u = User.objects.create_user(username=username, **settings)
                if cat == 'STAFF':
                    u.is_staff=True
                    u.save()
                    log.log(f'Staff user `{u}` added.')
                elif cat == 'USER':
                    log.log(f'User `{u}` added.')

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
        create_users(USERS)