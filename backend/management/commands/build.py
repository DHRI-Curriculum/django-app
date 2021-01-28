from django.core.management import BaseCommand, call_command

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Shortcut to run through all the build commands in the correct order'

    def handle(self, *args, **options):
        call_command('buildgroups')
        call_command('buildusers')
        call_command('buildglossary')
        call_command('buildinstalls')
        call_command('buildinsights')
        call_command('buildrepo', '--reset') #TODO: Make this force its way through (overriding existing folders.)
        call_command('buildblurbs')