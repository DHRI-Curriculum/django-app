from glossary.models import Term
from resource.models import Resource
from django.core.management import BaseCommand
from django.db.utils import IntegrityError
from backend.settings import BUILD_DIR
from backend.logger import Logger, Input
from backend.dhri_utils import dhri_slugify
from ._shared_functions import test_for_required_files, get_yaml

SAVE_DIR = f'{BUILD_DIR}_meta/glossary'
FULL_PATH = f'{SAVE_DIR}/glossary.yml'
REQUIRED_PATHS = [
    (SAVE_DIR,
     f'The required directory ({SAVE_DIR}) does not exist. Did you run `python manage.py buildglossary` before you ran this command?'),
    (FULL_PATH,
     f'The required data file ({FULL_PATH}) does not exist. Did you run `python manage.py buildglossary` before you ran this command?')
]


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with glossary information into the database'
    requires_migrations_checks = True
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
                     force_verbose=options.get('verbose'),
                     force_silent=options.get('silent')
                     )
        input = Input(path=__file__)

        test_for_required_files(REQUIRED_PATHS=REQUIRED_PATHS, log=log)
        data = get_yaml(FULL_PATH, log=log)

        for termdata in data:
            try:
                term, created = Term.objects.get_or_create(term=termdata.get('term'))
            except IntegrityError:
                try:
                    term = Term.objects.get(slug=dhri_slugify(termdata.get('term')))
                except:
                    log.error('An unknown error occurred. Try')

            term.term = termdata.get('term')
            term.explication = termdata.get('explication')
            term.save()

            if not created and not options.get('forceupdate'):
                choice = input.ask(
                    f'Term `{termdata.get("term")}` already exists. Update with new definition? [y/N]')
                if choice.lower() != 'y':
                    continue

            Term.objects.filter(term=termdata.get('term')).update(
                explication=termdata.get('explication')
            )

            term.refresh_from_db()

            for cat in ['tutorials', 'readings']:
                if termdata.get(cat):
                    category, add_field = None, None
                    if cat == 'tutorials':
                        category = Resource.TUTORIAL
                        add_field = term.tutorials
                    elif cat == 'readings':
                        category = Resource.READING
                        add_field = term.readings

                    for point in termdata.get(cat):
                        if not add_field or not category:
                            log.error('Cannot interpret category `{cat}`. Make sure the script is correct and corresponds with the database structure.')

                        try:
                            obj, created = Resource.objects.update_or_create(
                                category=category,
                                title=point.get('linked_text'),
                                url=point.get('url'),
                                annotation=point.get('annotation')
                            )
                            if obj not in add_field.all():
                                add_field.add(obj)
                        except IntegrityError:
                            obj = Resource.objects.get(
                                category=category,
                                title=point.get('linked_text'),
                                url=point.get('url'),
                            )
                            obj.annotation = point.get('annotation')
                            if obj not in add_field.all():
                                add_field.add(obj)
                            log.info(f'Another resource with the same URL, title, and category already existed so updated with a new annotation: **{point.get("linked_text")} (old)**\n{point.get("annotation")}\n-------\n**{obj.title} (new)**\n{obj.annotation}')

        log.log('Added/updated terms: ' +
                                 ', '.join([x.get('term') for x in data]))

        if log._save(data='buildusers', name='warnings.md', warnings=True) or log._save(data='buildusers', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' +
                    log.LOG_DIR, force=True)
