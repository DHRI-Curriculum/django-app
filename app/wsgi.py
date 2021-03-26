"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

### Reclaim Cloud (Jelastic) specific runtime information ##############

# Here's the activation of the environment. In `activate_this.py`, you should add lines that contain the secret keys below
#    os.environ["SECRET_KEY"] = '<insert secret key>'
#    os.environ["EMAIL_HOST_USER"] = '<insert email username>'
#    os.environ["EMAIL_HOST_PASSWORD"] = '<insert email password>'
#    os.environ["GITHUB_TOKEN"] = '<insert github token>'

import os
import sys

virtenv_dir = os.path.expanduser('~') + '/virtenv/'
virtualenv = os.path.join(virtenv_dir, 'bin/activate_this.py')

try:
    exec(compile(open(virtualenv, "rb").read(), virtualenv, 'exec'), dict(__file__=virtualenv)) # This will only work on Python 3
except IOError:
    pass # TODO: We might want to do something here... exit application?

sys.path.append(os.path.expanduser('~'))
sys.path.append(os.path.expanduser('~') + '/ROOT/')

#########################################################################

### Django standard runtime information #################################

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

application = get_wsgi_application()

#########################################################################
