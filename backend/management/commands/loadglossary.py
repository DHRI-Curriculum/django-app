from django.core.management import BaseCommand
from backend.dhri_settings import GLOSSARY_REPO
from backend.dhri.log import Logger, log_created
from backend.models import Term
from backend.dhri.loader import GlossaryLoader


log = Logger(name='loadglossary')


def create_terms(GLOSSARY_REPO=GLOSSARY_REPO):
    loader = GlossaryLoader()


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Create default pages'

    def handle(self, *args, **options):
        create_terms(GLOSSARY_REPO)