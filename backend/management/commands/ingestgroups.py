from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger, Input
from ._shared import test_for_required_files, get_yaml, get_name

log = Logger(name=get_name(__file__))
input = Input(name=get_name(__file__))
SAVE_DIR = f'{settings.BASE_DIR}/_preload/_meta/users'
FULL_PATH = f'{SAVE_DIR}/groups.yml'
REQUIRED_PATHS = [
    (SAVE_DIR, f'The required directory ({SAVE_DIR}) does not exist. Did you run `python manage.py buildgroups` before you ran this command?'),
    (FULL_PATH, f'The required data file ({FULL_PATH}) does not exist. Did you run `python manage.py buildgroups` before you ran this command?')
]


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with groups information into the database'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')

    def handle(self, *args, **options):
        test_for_required_files(REQUIRED_PATHS=REQUIRED_PATHS, log=log)
        data = get_yaml(f'{FULL_PATH}')

        for group_name, permission_set in data.items():
            group, created = Group.objects.get_or_create(name=group_name)

            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Group `{group_name}` already exists. Update with new information? [y/N]')
                if choice.lower() != 'y':
                    continue

            for codename in permission_set:
                try:
                    # Find permission object and add to group
                    perm = Permission.objects.get(codename=codename)
                    group.permissions.add(perm)
                    log.log(f'Adding {codename} to group {group.__str__()}.')
                except Permission.DoesNotExist:
                    log.error(f'{codename} not found.')
