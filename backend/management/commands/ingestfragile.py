import pathlib
import os
from feedback.models import Issue
from learner.models import Profile, Progress
from workshop.models import Workshop
from lesson.models import Lesson
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from backend.logger import Logger, Input
from .buildfragile import data as built_data
from backend.settings import get_settings


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with fragile database information back into the database'
    requires_migrations_checks = True
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__, force_verbose=options.get('verbose'), force_silent=options.get('silent'))
        input = Input(path=__file__)

        files = {x: y['data_file'] for x, y in built_data.items() if os.path.exists(y['data_file'])}
        raw = get_settings(files)

        for cat, data in raw.items():
            model = built_data[cat]['model']
            if model == Workshop:
                for obj in data:
                    Workshop.objects.filter(name=obj['fields']['name']).update(views=obj['fields']['views'])
                log.log(f'Loaded Workshop fragile data ({len(data)} objects).')
            elif model == Progress:
                for obj in data:
                    profile, updated = Profile.objects.get_or_create(user__first_name=obj['fields']['profile'][0], user__last_name=obj['fields']['profile'][1])
                    workshop = Workshop.objects.get_by_natural_key(obj['fields']['workshop'])
                    Progress.objects.update_or_create(profile=profile, workshop=workshop, defaults={
                        'page': obj['fields']['page'],
                        'modified': obj['fields']['modified']
                    })
                log.log(f'Loaded Progress fragile data ({len(data)} objects).')
            elif model == Issue:
                for obj in data:
                    lesson = Lesson.objects.get_by_natural_key(obj['fields']['lesson'])
                    user = User.objects.get(username=obj['fields']['user'][0])
                    issue, created = Issue.objects.get_or_create(workshop=workshop, lesson=lesson, user=user, website=obj['fields']['website'], open=obj['fields']['website'], comment=obj['fields']['comment'])
                log.log(f'Loaded Issue fragile data ({len(data)} objects).')
            else:
                log.error(f'Could not process some of the fragile data. This likely means that you have created ways to save fragile data but not built a way to ingest the fragile data back into the database. Revisit the code for ingestfragile command (backend.management.commands.ingestfragile) and ensure all is well.')

        # Delete all files with fragile data
        [file.unlink() for file in files.values()]

        log.log(f'Ingested all the fragile data back into the database. ({len(files)} files processed.)')