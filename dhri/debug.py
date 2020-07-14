from dhri.settings import DEBUG, AUTO_RESET, DJANGO_PATHS
from dhri.interaction import Logger
from django.db.utils import OperationalError
from pathlib import Path

log = Logger(name='debug')


def erase_migrations():
    p = Path(__file__).resolve()
    p = p.parent.parent
    app_path = Path(p) / 'app'
    manage = Path(app_path) / 'manage.py'
    sql = Path(app_path) / '/db.sqlite3'

    for app in ['assessment', 'frontmatter', 'praxis', 'workshop', 'lesson']:
        path = Path(app_path) / f'{app}/migrations/'
        for file in path.glob("*.py"):
            if not "__" in file.name:
                log.warning(f'Deleting file {file.name}')
                file.unlink()

def reset_all(kill=True) -> None:
    ''' development function - DO NOT USE IN PRODUCTION, EVER. '''

    if AUTO_RESET == False:
      _continue = inp.ask(message='Are you sure you want to reset the entire DHRI curriculum in the current Django database? (y/N) ', bold=True, color='red')
      if _continue.lower() != 'y':
        exit()
    else:
      log.warning('Resetting database (AUTO_RESET and DEBUG set to True in dhri.settings)...')

    from dhri.django import django
    from dhri.django.models import Workshop, Frontmatter, Project, Resource, Reading, Contributor, Question, Answer, QuestionType, LearningObjective, Praxis, Tutorial, Lesson, Challenge, Solution
    from dhri.settings import DJANGO_PATHS
    import os
    errors = []
    for _ in [Workshop, Frontmatter, Project, Resource, Reading, Contributor, Question, Answer, QuestionType, LearningObjective, Praxis, Tutorial, Lesson, Challenge, Solution]:
        try:
            _.objects.all().delete()
            log.log(f'All {_.__name__} deleted.', kill=not AUTO_RESET)
        except OperationalError:
            errors.append(_)

    if errors:
        log.error(f"{len(errors)} errors occurred.", kill=False)
        log.warning("Trying to run migrations... If it fails, run them manually")
        me = Path(__file__).absolute().parent.parent
        MANAGE = DJANGO_PATHS.get("MANAGE")
        MANAGE = MANAGE.relative_to(me)
        commands = f"python ./{MANAGE} makemigrations; python ./{MANAGE} migrate"
        os.system(commands)
    '''
    try:
        sql.unlink()
    except FileNotFoundError:
        log.warning("Could not find database file for deletion...")

    commands = [
        f'python {manage} makemigrations',
        f'python {manage} migrate',
    ]
    os.system(commands[0])
    os.system(commands[1])
    exit()
    '''


if DEBUG == True:
    for path in DJANGO_PATHS:
        if not Path(DJANGO_PATHS[path]).exists():
            log.warning(f"File/directory {DJANGO_PATHS[path]} must exist.")
    reset_all()
