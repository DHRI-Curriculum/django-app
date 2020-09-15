from django.core.management import BaseCommand
from django.contrib.auth.models import User
from backend.dhri_settings import AUTO_USERS
from backend.dhri.log import Logger
from backend.models import Workshop, Blurb


log = Logger(name='loadblurbs')


def create_blurbs(AUTO_USERS=AUTO_USERS):
    for cat in list(AUTO_USERS.keys()):
        for u in AUTO_USERS[cat]:
            if u.get('blurb'):
                user = User.objects.get(username=u.get('username'))
                if user:
                    text = u.get('blurb', {'text': None, 'workshop': None}).get('text')
                    workshop = u.get('blurb', {'text': None, 'workshop': None}).get('workshop')
                    if text and workshop:
                        try:
                            w = Workshop.objects.get(slug=workshop)
                        except:
                            w = None
                        if w:
                            obj, created = Blurb.objects.get_or_create(
                                workshop = w,
                                user = user,
                                defaults = {
                                    'text': text
                                }
                            )
                            log.created(created, 'Blurb', obj.workshop, obj.id)
                        else:
                            log.error(f'Workshop {workshop} does not exist. You may need to run `manage.py setup --repo {workshop}` before you run this command.', kill=False)
                    else:
                        log.error(f'Blurb data for user `{u.get("username")}` is not complete. You need to provide text and a workshop shortcode.', kill=False)
                else:
                    log.error(f'User `{u.get("username")}` does not exist. You may need to run `manage.py loadusers` before you run this command.', kill=False)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Create blurbs'

    def handle(self, *args, **options):
        create_blurbs(AUTO_USERS)