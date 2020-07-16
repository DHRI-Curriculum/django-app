# backend/management/commands/create_groups.py
from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission
from backend.dhri_settings import GROUPS_PERMISSIONS
from backend.dhri.log import Logger


log = Logger(name='loadgroups')


def create_groups(GROUPS_PERMISSIONS=GROUPS_PERMISSIONS):
    # Loop groups
    for group_name in GROUPS_PERMISSIONS:

        # Get or create group
        group, created = Group.objects.get_or_create(name=group_name)

        # Loop models in group
        for model_cls in GROUPS_PERMISSIONS[group_name]:

            # Loop permissions in group/model
            for perm_index, perm_name in enumerate(GROUPS_PERMISSIONS[group_name][model_cls]):

                # Generate permission name as Django would generate it
                codename = perm_name + '_' + model_cls._meta.model_name

                try:
                    # Find permission object and add to group
                    perm = Permission.objects.get(codename=codename)
                    group.permissions.add(perm)
                    log.log(f'Adding {codename} to group {group.__str__()}.')
                except Permission.DoesNotExist:
                    log.error(f'{codename} not found.')


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Create default groups'

    def handle(self, *args, **options):
        create_groups(GROUPS_PERMISSIONS)