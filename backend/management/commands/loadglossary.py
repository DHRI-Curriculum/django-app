from django.core.management import BaseCommand
from backend.dhri_settings import GLOSSARY_REPO
from backend.dhri.log import Logger, log_created
from backend.models import Term, Reading, Tutorial
from backend.dhri.loader import GlossaryLoader, process_links


log = Logger(name='loadglossary')


def create_terms(glossary_repo=GLOSSARY_REPO):
    loader = GlossaryLoader(glossary_repo)
    # TODO: #166 Add something in the Glossary app that makes a clearer connection to which workshops that are linked to each term. Perhaps each lesson can have a ManyToMany relationship to the Terms?

    for term in loader.all_terms:

        t, created = Term.objects.get_or_create(
            term=loader.terms[term].term,
            explication=loader.terms[term].explication
        )
        log.created(created, 'Term', t.term, t.id)

        for d in loader.terms[term].readings:
            obj, created = Reading.objects.get_or_create(annotation = d['annotation'], title = d['linked_text'], url = d['url'])
            log.created(created, 'Reading', obj.title, obj.id)
            t.readings.add(obj)

        for d in loader.terms[term].tutorials:
            obj, created = Tutorial.objects.get_or_create(annotation = d['annotation'], label = d['linked_text'], url = d['url'])
            log.created(created, 'Tutorial', obj.label, obj.id)
            t.tutorials.add(obj)


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

            GlossaryLoader(force_download=True)
            log.log(f'Glossary cache removed.', force=True)

        create_terms()