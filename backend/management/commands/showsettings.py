from django.core.management import BaseCommand
from django.contrib.auth.models import User, Group
from backend.dhri_settings import AUTO_REPOS
from backend.dhri.log import Logger


log = Logger(name='loadusers')

def print_row(col1, col2, col3, col1_w=15, col2_w=30, col3_w=30):
    print(f" %-{col1_w}s %-{col2_w}s %-{col3_w}s" % (col1, col2, col3))

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Show default settings'

    def add_arguments(self, parser):
        parser.add_argument('--repo', action='store_true')

    def handle(self, *args, **options):
        if not options.get('repo', False):
            options['repo'] = True # Automatic setting to `repo`

        i = 0
        if options.get('repo', False):
            for r in AUTO_REPOS:
                i += 1
                repo, branch = r
                print_row(i, repo, branch, col1_w=3)