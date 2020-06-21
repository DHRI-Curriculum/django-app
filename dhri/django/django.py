import django
import os
import sys

from dhri.interaction import Logger

log = Logger(name="django")

log.log(f'Setting up database interaction...')

sys.path.append('./app')
os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings'
django.setup()

from dhri.django.models import *
