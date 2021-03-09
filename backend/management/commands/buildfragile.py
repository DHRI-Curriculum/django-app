from django.core.management import BaseCommand
from django.core import serializers
from backend.settings import BUILD_DIR
from backend.logger import Logger
from feedback.models import Issue
from learner.models import Progress
from workshop.models import Workshop
import pathlib


SAVE_DIR = f'{BUILD_DIR}_fragile'
data = {
    'workshop_views': {
        'model': Workshop,
        'fields': ('views', 'name'),
        'use_natural_primary_keys': True,
        'use_natural_foreign_keys': True,
        'data_file': pathlib.Path(SAVE_DIR) / pathlib.Path('workshop_views.yml')
    },

    'progress_data': {
        'model': Progress,
        'fields': ('profile', 'workshop', 'page', 'modified'),
        'use_natural_primary_keys': True,
        'use_natural_foreign_keys': True,
        'data_file': pathlib.Path(SAVE_DIR) / pathlib.Path('progress_data.yml')
    },

    'all_issues': {
        'model': Issue,
        'fields': ('lesson', 'workshop', 'user', 'website', 'open', 'comment'),
        'use_natural_primary_keys': True,
        'use_natural_foreign_keys': True,
        'data_file': pathlib.Path(SAVE_DIR) / pathlib.Path('all_issues.yml')
    }
}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Builds internal DHRI YAML data files with fragile database information which should be read back into the database at the end of an ingestion-process'

    def add_arguments(self, parser):
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__, force_verbose=options.get('verbose'), force_silent=options.get('silent'))
        log.log('Building files with fragile data... Please be patient as this can take some time.')

        if pathlib.Path(SAVE_DIR).exists():
            # Make sure it is empty as we don't want to save any old fragile data information
            [file.unlink() for file in pathlib.Path(SAVE_DIR).glob('*')]    
        
        if not pathlib.Path(SAVE_DIR).exists():
            pathlib.Path(SAVE_DIR).mkdir(parents=True)

        for cat in data:
            dataset = data[cat]['model'].objects.all()
            if not dataset.count():
                log.warning(data[cat]['model']._meta.object_name + ' has no objects. No file will be written.')
            else:
                d = serializers.serialize('yaml', dataset, fields=data[cat]['fields'], use_natural_primary_keys=data[cat]['use_natural_primary_keys'], use_natural_foreign_keys=data[cat]['use_natural_foreign_keys'])
                with open(data[cat]['data_file'], 'w+') as f:
                    f.write(d)
                
                log.log(f'Saved {data[cat]["model"]._meta.object_name} fragile data in: {data[cat]["data_file"]}')
