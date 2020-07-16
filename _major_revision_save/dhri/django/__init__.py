from dhri.interaction import Logger
import json
from django.core import serializers
from pathlib import Path
from dhri.settings import FIXTURE_PATH

class Fixture():

    log = Logger(name='autoname', bypass_verbose=True)

    def __init__(self, *args, **kwargs):
        self.objects = []
        if 'name' in kwargs: self.log.name = kwargs['name']

    def save(self, path=''):
        self.log.log(f'Generating fixtures file for Django...')
        all_objects_dict = json.loads(serializers.serialize('json', self.objects, ensure_ascii=False))
        if path != '':
            path = Path(path)
        else:
            path = Path(FIXTURE_PATH)
        path.write_text(json.dumps(all_objects_dict))
        self.log.log(f'Fixture file generated: {FIXTURE_PATH}')

    def append(self, object):
        pass

    def extend(self, object_list:list):
        pass

    def add(self, *args, **kwargs):
        if kwargs.get('workshop') != None:
            self.objects.append(kwargs['workshop'])
            self.log.log(f'Workshop {kwargs["workshop"].id} added to fixture.')

        if kwargs.get('frontmatter') != None:
            self.objects.append(kwargs['frontmatter'])
            self.log.log(f'Frontmatter {kwargs["frontmatter"].id} added to fixture.')

        if kwargs.get('praxis') != None:
            self.objects.append(kwargs['praxis'])
            self.log.log(f'Praxis {kwargs["praxis"].id} added to fixture.')

        if kwargs.get('collector') != None:
            for x, _ in kwargs['collector'].items():
                self.objects.extend([x for x in _])
                self.log.log(f'{x} added to fixture.')