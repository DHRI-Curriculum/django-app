from django.core.management import BaseCommand
from backend.dhri_settings import GLOSSARY_REPO
from backend.dhri.log import Logger, log_created
from backend.models import Term, Reading, Tutorial
from backend.dhri.loader import GlossaryLoader, process_links

from pprint import pprint

log = Logger(name='loadglossary')


def create_terms(GLOSSARY_REPO=GLOSSARY_REPO):
    loader = GlossaryLoader()

    for _, data in loader.sections.items():
        readings, tutorials = list(), list()

        if data.get('readings'):
            readings = data.pop('readings')

        if data.get('tutorials'):
            tutorials = data.pop('tutorials')

        if len(data) == 1:
            header = [_ for _ in data.keys()][0]
            content = [_ for _ in data.values()][0]
        else:
            log.error(f'Too many headers in the glossary term `{term}`. Please make sure the markdown file follows conventions.')

        term, created = Term.objects.get_or_create(
            term=header,
            explication=content
        )
        log.created(created, 'Term', term.term, term.id)

        for annotation in readings:
            title, url = process_links(annotation, 'reading')
            obj, created = Reading.objects.get_or_create(annotation = annotation, title = title, url = url)
            log.created(created, 'Reading', obj.title, obj.id)
            # title, url = process_links(reading, 'reading')
            # obj = Reading.objects.get_or_create(title=title, url=url)
            term.readings.add(obj)

        for annotation in tutorials:
            label, url = process_links(annotation, 'tutorial')
            obj, created = Tutorial.objects.get_or_create(annotation = annotation, label = label, url = url)
            # title, url = process_links(tutorial, 'tutorial')
            # obj = Tutorial.objects.get_or_create(title=title, url=url)
            log.created(created, 'Tutorial', obj.label, obj.id)
            term.tutorials.add(obj)

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('--wipe', action='store_true')

    help = 'Create glossary words'

    def handle(self, *args, **options):
        if options.get('wipe', False):
            Term.objects.all().delete()
            log.log(f'All Terms removed.', force=True)
        create_terms(GLOSSARY_REPO)