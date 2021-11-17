from django.conf import settings as django_settings
from django.apps import apps
from backend.settings import BUILD_DIR

import pathlib
import yaml
import os

all_apps = [x.split('.')[0] for x in django_settings.INSTALLED_APPS if not x.startswith('django') and '.apps.' in x]
_ = [apps.all_models[x] for x in all_apps]
all_models = list()
[all_models.extend(list(x.values())) for x in _]

WORKSHOPS_DIR = BUILD_DIR + '_workshops'
GLOSSARY_FILE = BUILD_DIR + '_meta/glossary/glossary.yml'


def test_for_required_files(REQUIRED_PATHS=[], log=None):
    ''' Tests whether all the paths in a list of paths exists. List provided should be a list of tuples with (`path`, `potential error message`). Log provided should be of backend.logger.Logger type '''
    for test in REQUIRED_PATHS:
        path, error_msg = test
        if not pathlib.Path(path).exists():
            if log:
                log.error(error_msg)
            else:
                exit(error_msg)

    return True


def get_yaml(file, log=None, catch_error=False):
    ''' Returns the contents of any given YAML file as a dictionary '''
    try:
        with open(file, 'r+') as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)
    except FileNotFoundError:
        error_msg = f'A required datafile was not found ({file}). Try running python manage.py build before you run this command. If it does not work, consult the documentation.'
        if not log:
            if catch_error:
                raise FileNotFoundError(error_msg)
            else:
                exit(error_msg)
        else:
            if catch_error:
                raise FileNotFoundError(error_msg)
            else:
                log.error(error_msg)


def get_all_existing_workshops(specific_names=None, log=None):
    ''' Returns a list of all of the names in the workshops directory (provided in WORKSHOPS_DIR) or, if provided a list of specific_names, will check whether they exist. '''
    if not specific_names:
        return [(x, f'{WORKSHOPS_DIR}/{x}') for x in os.listdir(WORKSHOPS_DIR) if not x.startswith('.')]
    
    _ = list()
    for name in specific_names:
        if name in os.listdir(WORKSHOPS_DIR):
            _.append((name, f'{WORKSHOPS_DIR}/{name}'))
        else:
            error_msg = f'The workshop `{name}` failed to ingest as the workshop\'s directory has yet to be created. Try running python manage.py buildworkshop --name {name} before running this command again.'
            if log:
                log.error(error_msg)
            else:
                exit(error_msg)
    return _


def crop_and_save(source, target, MAX_SIZE=400):
    from PIL import Image
    ''' Takes a source path, crops it as a square from the center with a max width/height of MAX_SIZE pixels, and saves it to target path'''

    def _crop_center(pil_img, crop_width, crop_height):
        # https://note.nkmk.me/en/python-pillow-square-circle-thumbnail/
        img_width, img_height = pil_img.size
        return pil_img.crop(((img_width - crop_width) // 2,
                            (img_height - crop_height) // 2,
                            (img_width + crop_width) // 2,
                            (img_height + crop_height) // 2))

    with open(source, 'rb') as f:
        cropped_img = Image.open(f)
        w, h = cropped_img.size
        if w != h:
            cropped_img = _crop_center(cropped_img, min(cropped_img.size), min(cropped_img.size))  # crop to square from center!
        cropped_img = cropped_img.resize(
            (MAX_SIZE, MAX_SIZE),
            Image.LANCZOS
        )
        cropped_img.save(target, 'jpeg', quality=50)
    return True

