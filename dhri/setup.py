from dhri.interaction import get_or_default, Logger
from dhri.settings import DJANGO_PATHS
import time, os

log = Logger(name='setup')

def setup(collect_workshop_slugs:list):
    if DJANGO_PATHS["DB"].exists():
        _ = get_or_default('Do you want to remove the existing database file and build a new one from the downloaded data? [n/Y] ', 'y', color='red').lower()
        if _.lower() == "y":
            DJANGO_PATHS["DB"].unlink()
            log.log(f'Database file {DJANGO_PATHS["DB"]} removed.')
    _ = get_or_default('Do you want to run Django migrations automatically? [n/Y] ', 'y', color='red').lower()
    if _.lower() == "y":
        os.system(f'python {DJANGO_PATHS["MANAGE"]} makemigrations')
        log.log(f'Migrations created.')
        os.system(f'python {DJANGO_PATHS["MANAGE"]} migrate')
        log.log(f'Database migrated.')
        os.system(f'python {DJANGO_PATHS["MANAGE"]} loaddata ./app/fixtures.json')
        log.log(f'Fixtures loaded.')
        _ = get_or_default('Do you want to set up superuser? [n/Y] ', 'y', color='red').lower()
        if _.lower() == "y":
            os.system(f'python {DJANGO_PATHS["MANAGE"]} createsuperuser')
        log.log(f'You should now be able to run in your command line:\npython {DJANGO_PATHS["MANAGE"]} runserver')
        log.log(f'Once you have it running, you can navigate to any of the following workshops:\n' + '- http://localhost:8000/workshop/' + '\n- http://localhost:8000/workshop/'.join(collect_workshop_slugs))