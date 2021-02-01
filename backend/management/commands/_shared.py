from django.utils.text import slugify
from django.conf import settings
import pathlib, yaml, re, os


WORKSHOPS_DIR = settings.BASE_DIR + '/_preload/_workshops'
GLOSSARY_FILE = settings.BASE_DIR + '/_preload/_meta/glossary/glossary.yml'


def test_for_required_files(REQUIRED_PATHS=[], log=None):
    for test in REQUIRED_PATHS:
        path, error_msg = test
        if not pathlib.Path(path).exists():
            return log.error(error_msg)

    return True


def get_yaml(file):
    try:
        with open(file, 'r+') as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)
    except FileNotFoundError:
        exit(f'A required datafile was not found ({file}). Try running python manage.py build before you run this command. If it does not work, consult the documentation.')


def get_name(path):
    return path.split('/')[-1].replace('.py', '')


def dhri_slugify(string: str) -> str:  # TODO: Move to backend.dhri.text
    # first replace any non-OK characters [/] with space
    string = re.sub(r'[\/\-\–\—\_]', ' ', string)

    # then replace too many spaces with one space
    string = re.sub(r'\s+', ' ', string)

    # then replace space with -
    string = re.sub(r'\s', '-', string)

    # then replace any characters that are not in ALLOWED charset with nothing
    string = re.sub(r'[^a-zA-Z\-\s]', '', string)

    # finally, use Django's slugify
    string = slugify(string)

    return string


def get_all_existing_workshops(specific_names=None, log=None):
    if not specific_names:
        return [(x, f'{WORKSHOPS_DIR}/{x}') for x in os.listdir(WORKSHOPS_DIR) if not x.startswith('.')]
    
    _ = list()
    for name in specific_names:
        if name in os.listdir(WORKSHOPS_DIR):
            _.append((name, f'{WORKSHOPS_DIR}/{name}'))
        else:
            log.error(f'The workshop `{name}` failed to ingest as the workshop\'s directory has yet to be created. Try running python manage.py buildworkshop --name {name} before running this command again.')
    return _