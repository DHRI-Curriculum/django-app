from dhri.settings import DEBUG, AUTO_RESET
from dhri.interaction import Logger
from pathlib import Path

log = Logger(name='debug')

def reset_all(kill=True) -> None:
    ''' development function - DO NOT USE IN PRODUCTION, EVER. '''

    if AUTO_RESET == False:
      _continue = inp.ask(message='Are you sure you want to reset the entire DHRI curriculum in the current Django database? (y/N) ', bold=True, color='red')
      if _continue.lower() != 'y':
        exit()
    else:
      log.warning('Resetting database (AUTO_RESET and DEBUG set to True in dhri.settings)...')

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
    os.system(commands[0])
    os.system(commands[1])
    exit()
    '''

    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='admin').count():
        User.objects.create_superuser('admin', '', 'admin')


if DEBUG == True:
    reset_all()