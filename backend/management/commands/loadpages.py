from django.core.management import BaseCommand
from backend.dhri_settings import AUTO_PAGES
from backend.dhri.log import Logger, log_created
from backend.models import Page


log = Logger(name='loadpages')


def create_pages(AUTO_PAGES=AUTO_PAGES):
    for p in AUTO_PAGES:
        page, created = Page.objects.get_or_create(
            name = p.get('name', None),
            text = p.get('text', None),
            defaults = {
                'template': p.get('template', None),
                'slug': p.get('slug', None)
            }
        )
        log_created(created, 'Page', page.name, page.id, log)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Create default pages'

    def handle(self, *args, **options):
        create_pages(AUTO_PAGES)