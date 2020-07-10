from dhri.interaction import get_or_default, Logger
from dhri.settings import DJANGO_PATHS
import time, os
from pathlib import Path

log = Logger(name='setup')

def setup(collect_workshop_slugs:list):
    DB, MANAGE = DJANGO_PATHS.get("DB"), DJANGO_PATHS.get("MANAGE")

    if DB.exists():
        _ = get_or_default('Do you want to remove the existing database file and build a new one from the downloaded data? [n/Y] ', 'y', color='red').lower()
        if _.lower() == "y":
            DB.unlink()
            log.log(f'Database file {DB} removed.')
    _ = get_or_default('Note that this feature might not work perfectly yet, but do you want to run Django migrations automatically? [n/Y] ', 'y', color='red').lower()
    if _.lower() == "y":
        me = Path(__file__).absolute().parent.parent
        MANAGE = MANAGE.relative_to(me)
        commands = f"python ./{MANAGE} makemigrations; python ./{MANAGE} migrate; python {MANAGE} loaddata ./app/fixtures.json; python ./{MANAGE} createsuperuser"
        log.warning(f"If the commands do not work, you can run them on the command line like this:\n{commands}")
        log.warning(f"One reason why they might not work is because you have not activated the correct virtual environment.")
        os.system(commands)
        log.log(f"You should now be able to run the command: python ./{MANAGE} runserver")
        if len(collect_workshop_slugs):
            all_urls = "\n- http://localhost:8000/workshops/" + ("\n- http://localhost:8000/workshops/".join(collect_workshop_slugs))
            log.log(f"Once the server is up and running, you can visit:")
            print(all_urls)
    else:
        commands = f"python ./{MANAGE} makemigrations; python ./{MANAGE} migrate; python {MANAGE} loaddata ./app/fixtures.json; python ./{MANAGE} createsuperuser"
        log.warning(f"You should now manually run these commands on your command line:"
        print(commands)