from django.utils.text import slugify
from django.conf import settings
import pathlib, yaml, os, datetime

from django.apps import apps
all_apps = [x.split('.')[0] for x in settings.INSTALLED_APPS if not x.startswith('django') and '.apps.' in x]
_ = [apps.all_models[x] for x in all_apps]
all_models = list()
[all_models.extend(list(x.values())) for x in _]

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


class LogSaver():

    LOG_DIR = f'{settings.BASE_DIR}/_logs' # Can also be placed in _preload/_logs

    def _save(self, lst=[], data={}, name='log.md', warnings=True, logs=False, step='buildworkshop'):
        ''' Private function to save a list of warnings and logs'''

        if not lst and not warnings and not logs:
            return False
        elif not lst and warnings:
            lst = self.WARNINGS
        elif not lst and logs:
            lst = self.LOGS

        if not lst:
            return False

        if not pathlib.Path(self.SAVE_DIR).exists(): pathlib.Path(self.SAVE_DIR).mkdir(parents=True)
        with open(f'{self.SAVE_DIR}/{name}', 'w+') as f:
            if type(data) == dict and data.get("name"):
                f.write('# Workshop: [' + data.get("name") + '](https://www.github.com/' + data.get('parent_repo') + '/tree/' + data.get('parent_branch') + ')\n\n')
            elif type(data == str):
                f.write(f'# {data}\n\n')
            f.write('**Log file created:** ' + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S') + '\n\n')
            if warnings:
                f.write('## Warnings:\n\n')
            elif logs:
                f.write('## Logs:\n\n')
            else:
                f.write('## List:\n\n')
            f.write('[ ] ' + '\n- [ ] '.join(lst))
            f.write(f'\n\n---\n\nWarnings do not need to be resolved in order for the data to be correctly ingested but there may be issues that you want to resolve.\n\n')
            if step == 'buildworkshop' and type(data) == dict and data.get("name") and data.get("slug"):
                f.write(f'If you have finished resolving the warnings above (or if you do not wish to resolve the warnings), rerun the `buildworkshop` command, and then proceed with the ingestion of the workshop. You ingest the workshop by running either of the following two commands:\n- `python manage.py ingestworkshop --name {data.get("slug")}`\n- `python manage.py ingestworkshop --all`\n\nAdd the `--forceupdate` flag to any of them if you do not want to confirm all edits.')
        
        return True
