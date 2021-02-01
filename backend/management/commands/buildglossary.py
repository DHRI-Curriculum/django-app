from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger
from backend import dhri_settings
from backend.dhri.loader import GlossaryLoader
from ._shared import get_name
import yaml
import pathlib

SAVE_DIR = f'{settings.BASE_DIR}/_preload/_meta/glossary'
DATA_FILE = 'glossary.yml'


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from glossary repository (provided through dhri_settings.GLOSSARY_REPO)'

    def add_arguments(self, parser):
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(name=get_name(__file__), force_verbose=options.get('verbose'), force_silent=options.get('silent'))

        loader = GlossaryLoader(dhri_settings.GLOSSARY_REPO)

        glossary = list()

        for term in loader.all_terms:
            glossary.append({
                'term': loader.terms[term].term.strip(),
                'explication': loader.terms[term].explication.strip()
            })

        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
            file.write(yaml.dump(glossary))
