import argparse, json, os, re
from pathlib import Path

from dhri.settings import AUTO_RESET
from dhri.interaction import Logger, Input
from dhri.utils.regex import URL
from dhri.utils.exceptions import UnresolvedNameOrBranch

log = Logger(name="meta")


def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument('-d', '--download', type=str, help='download from a directory')
    g.add_argument('-f', '--file', type=str, help='load data from a file containing JSON with processed data from a DHRI curriculum')
    g.add_argument('-r', '--reset', action='store_true', help='reset the DHRI curriculum data in the database')
    
    g2 = g.add_argument_group()
    g2.add_argument('--dest', type = str, help = 'optional destination for download')
    
    return(parser)


def confirm_url(url: str) -> bool:
    """Confirm that the string tested is a URL"""
    if re.findall(URL, url):
        return(True)
    return(False)


def verify_url(url: str) -> str:
    if not confirm_url(url):
        log.error(f'You must provide a valid URL to a DHRI repository. {url} was not accepted.', raise_error=UnresolvedNameOrBranch)
    if not 'github' in url.lower():
        log.error(f'Your URL seems to not originate with Github. Currently, our curriculum only works with Github as backend.', raise_error=NotImplementedError)
    log.log(f'URL accepted: {url}')
    return(url)


def load_data(path: str) -> dict:
  log.log(f'Loading {path}')

  if not Path(path).exists():
    log.error(f'Could not find JSON file on path: {path}')

  data = json.loads(Path(path).read_text())
  return(data)


def test_path(path: str) -> bool:
    """Tests the pathname"""
    if not path.endswith('.json'):
        log.warning(f'The data file ({path}) is not saved as a .json file. It will work but it might be confusing.')
    return(True)


def save_data(path: str, data: dict) -> bool:
    test_path(path)
    Path(path).write_text(json.dumps(data))
    log.log(f'File saved to {path}')
    return(True)


def delete_data(path, auto=False):
    if auto == False:
      _continue = Input.ask(f'Are you sure you want to delete the data file ({path})? (y/N) ', bold=True, color='red')
      if _continue.lower() != 'y':
        exit()
    else:
      log.warning('Deleting file (DELETE_FILE set to True)...')
    
    Path(path).unlink()




def reset_all(kill=True) -> None:
    ''' development function - DO NOT USE IN PRODUCTION, EVER. '''

    if AUTO_RESET == False:
      _continue = Input.ask('Are you sure you want to reset the entire DHRI curriculum in the current Django database? (y/N) ', bold=True, color='red')
      if _continue.lower() != 'y':
        exit()
    else:
      log.warning('Resetting database (AUTO_RESET set to True)...')

    from dhri.django import django
    from dhri.django.models import Workshop, Frontmatter, Project, Resource, Reading, Contributor, Question, Answer, QuestionType, LearningObjective, Praxis, Tutorial
    for _ in [Workshop, Frontmatter, Project, Resource, Reading, Contributor, Question, Answer, QuestionType, LearningObjective, Praxis, Tutorial]:
        _.objects.all().delete()
        log.log(f'All {_.__name__} deleted.', kill=not AUTO_RESET)

    p = Path(__file__).resolve()
    p = p.parent.parent
    app_path = Path(p) / 'app'
    manage = Path(app_path) / 'manage.py'
    sql = Path(app_path) / '/db.sqlite3'

    for app in ['assessment', 'frontmatter', 'praxis', 'workshop']:
        path = Path(app_path) / f'{app}/migrations/'
        for file in path.glob("*.py"):
            if not "__" in file.name: 
                log.warning(f'Deleting file {file.name}')
                file.unlink()
    
    '''
    try:
        sql.unlink()
    except FileNotFoundError:
        log.warning("Could not find database file for deletion...")

    commands = [
        f'python {manage} makemigrations',
        f'python {manage} migrate',
    ]
    print(commands[0])
    os.system(commands[0])
    print(commands[1])
    os.system(commands[1])
    exit()
    '''

    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='admin').count():
        User.objects.create_superuser('admin', '', 'admin')
