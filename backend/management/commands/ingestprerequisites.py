from workshop.models import Prerequisite, URL, Workshop, Frontmatter
from insight.models import Insight
from install.models import Software
from django.core.management import BaseCommand
from backend.logger import Logger
from django.core.exceptions import FieldError
from ._shared_functions import get_yaml, get_all_existing_workshops


def search_workshop(potential_name, for_workshop=None, log=None, DATAFILE=None):
    potential_name = potential_name.lower()
    searches = [
        potential_name,
        potential_name.replace('intro to the', ''),
        potential_name.replace('intro to', ''),
        potential_name.replace('introduction to the', ''),
        potential_name.replace('introduction to', ''),
    ]
    finders = [Workshop.objects.filter(name__icontains=x) for x in searches]
    # we have at least one workshop that matches the searches above
    if [x for x in finders if x.count() > 0] and [x for x in finders if x.count() == 1]:
        linked_workshop = [x for x in finders if x.count() == 1][0][0]
        return linked_workshop
    elif [x for x in finders if x.count() > 0]:
        log.error(
            f'There are multiple workshops in the database that match the linked workshop in the prerequisite for {for_workshop}. Please disambiguate by adjusting the repository or the local datafile ({DATAFILE}), and after that, rerun python manage.py ingestworkshop --name {for_workshop} followed by python manage.py ingestprerequisites. The following searches were conducted: {searches}')
        return False

    log.error(
        f'Unable to find workshops matching the linked workshop in the prerequisite for {for_workshop}. Please check for misspelling or adjust the repository or the local datafile ({DATAFILE}). After that, rerun python manage.py ingestworkshop --name {for_workshop} followed by python manage.py ingestprerequisites. The following searches were conducted: {searches}')
    return False


def get_fragments_of_name(name):
    if len(name) > 30:
        return [
            ''.join(name[:10]),
            ''.join(name[-10:]),
        ]
    return []


def clean_up(category, linked_workshop, linked_insight, url):
    # Remove the excess ones, and only keep the last one..
    all = Prerequisite.objects.filter(category=category, 
        linked_workshop=linked_workshop, 
        linked_insight=linked_insight, 
        url=url)
    num = all.count()
    if num > 1:
        for p in Prerequisite.objects.filter(category=category, 
            linked_workshop=linked_workshop, 
            linked_insight=linked_insight, 
            url=url)[0:num-1]:
                p.delete()
    
    Prerequisite.objects.filter(category=Prerequisite.EXTERNAL_LINK, url__icontains='dhinstitutes.org/shortcuts/').delete()

def search_install(potential_name, for_workshop=None, log=None, DATAFILE=None):
    potential_name = potential_name.lower()
    searches = [
        potential_name,
        potential_name.replace('installing', ''),
        potential_name.replace('install', ''),
    ]
    searches.extend(get_fragments_of_name(potential_name))
    finders = [Software.objects.filter(name__icontains=x) for x in searches]
    if [x for x in finders if x.count() > 0]:
        # we have at least one software installation that matches the searches above
        if [x for x in finders if x.count() >= 1]:
            linked_installs = [x for x in finders if x.count() >= 1][0]
            return linked_installs
    log.error(
        f'Unable to find installation instructions matching the linked workshop in the prerequisite for {for_workshop}. Please check for misspelling or adjust the repository or the local datafile ({DATAFILE}). After that, rerun python manage.py ingestworkshop --name {for_workshop} followed by python manage.py ingestprerequisites. The following searches were conducted: {searches}')
    return False


def search_insight(potential_name, potential_slug_fragment, for_workshop=None, log=None, DATAFILE=None):
    potential_name = potential_name.lower()
    searches = [
        potential_name,
        potential_name.replace('short introduction to', ''),
        potential_name.replace('introduction to', ''),
    ]
    searches.extend(get_fragments_of_name(potential_name))
    finders = [Insight.objects.filter(title__icontains=x) for x in searches]
    if [x for x in finders if x.count() > 0]:
        # we have at least one insight that matches the searches above
        if [x for x in finders if x.count() > 0] and [x for x in finders if x.count() == 1]:
            linked_insight = [x for x in finders if x.count() == 1][0][0]
            return linked_insight
        elif [x for x in finders if x.count() > 0]:
            log.error(
                f'There are multiple insights in the database that match the linked insight in the prerequisite for {for_workshop}. Please disambiguate by adjusting the repository or the local datafile ({DATAFILE}), and after that, rerun python manage.py ingestworkshop --name {for_workshop} followed by python manage.py ingestprerequisites. The following searches were conducted: {searches}')
            return False

    else:
        searches = [potential_slug_fragment]
        finders = [Insight.objects.filter(
            slug__icontains=potential_slug_fragment) for x in searches]
        if [x for x in finders if x.count() > 0]:
            # we have at least one insight that matches the searches above
            if [x for x in finders if x.count() > 0] and [x for x in finders if x.count() == 1]:
                linked_insight = [x for x in finders if x.count() == 1][0][0]
                return linked_insight
            elif [x for x in finders if x.count() > 0]:
                log.error(
                    f'There are multiple insights in the database that match the linked insight in the prerequisite for {for_workshop}. Please disambiguate by adjusting the repository or the local datafile ({DATAFILE}), and after that, rerun python manage.py ingestworkshop --name {for_workshop} followed by python manage.py ingestprerequisites. The following searches were conducted: {searches}')
                return False

    log.error(
        f'Unable to find insights matching the linked insight in the prerequisite for {for_workshop}. Please check for misspelling or adjust the repository or the local datafile ({DATAFILE}). After that, rerun python manage.py ingestworkshop --name {for_workshop} followed by python manage.py ingestprerequisites. The following searches were conducted: {searches}')
    return False


def clean_name(name):
    name = name.lower()
    for s, r in {'installing': '', 'short introduction to': '', 'introduction': '', 'intro': '', ' to ': ''}.items():
        name = name.replace(s, r)
    return name.strip()


def search(obj, name, log=None):
    for field_name in ['name', 'title']:
        if field_name in [field.name for field in obj._meta.get_fields()]:
            if obj.objects.filter(**{f'{field_name}__iexact': name}).count() == 1:
                return obj.objects.get(**{f'{field_name}__iexact': name})

            if obj.objects.filter(**{f'{field_name}__iexact': clean_name(name)}).count() == 1:
                return obj.objects.get(**{f'{field_name}__iexact': clean_name(name)})
            
            # search whether there are objects obj that contain the field_name in their title
            if obj.objects.filter(**{f'{field_name}__icontains': clean_name(name)}).count() == 1:
                return obj.objects.get(**{f'{field_name}__icontains': clean_name(name)})
            elif obj.objects.filter(**{f'{field_name}__icontains': clean_name(name)}).count() > 1:
                print(obj.objects.filter(**{f'{field_name}__icontains': clean_name(name)}))
                log.error(f'Searching for {obj.__name__} with the name `{name}` (cleaned version `{clean_name(name)}`) turns up multiple results. Please write a more specific name for the prerequired {obj.__name__} in the markdown on GitHub and rerun the build and ingest commands for the prerequisites.')

    log.error(f'Searching for {obj.__name__} with the name `{name}` (cleaned version `{clean_name(name)}`) cannot be found. Please write a more specific name for the prerequired {obj.__name__} in the markdown on GitHub and rerun the build and ingest commands for the prerequisites.')


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with information about all the existing prerequisites into the database'
    requires_migrations_checks = True
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true')
        parser.add_argument('--name', nargs='+', type=str)
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
            force_verbose=options.get('verbose'),
            force_silent=options.get('silent')
        )

        workshops = get_all_existing_workshops()

        if options.get('name'):
            workshops = get_all_existing_workshops(options.get('name'))

        for _ in workshops:
            slug, path = _
            workshop, frontmatter = None, None
            DATAFILE = f'{path}/{slug}.yml'

            superdata = get_yaml(DATAFILE, log=log)

            # Separate out data
            frontmatterdata = superdata.get('sections').get('frontmatter')
            name = superdata.get('name')

            # 1. FIND WORKSHOP
            try:
                workshop = Workshop.objects.get(name=name)
            except:
                log.error(f'The workshop `{slug}` could not be found. Make sure you ran python manage.py ingestworkshop --name {slug} before running this command.')

            # 2. FIND FRONTMATTER
            try:
                frontmatter = Frontmatter.objects.get(workshop=workshop)
            except:
                log.error(f'Frontmatter for the workshop `{slug}` could not be found. Make sure you ran python manage.py ingestworkshop --name {slug} before running this command.')

            for prereqdata in frontmatterdata.get('prerequisites'):

                linked_workshop, linked_software, linked_insight, linked_external = None, None, None, None
                url = prereqdata.get('url')
                type = prereqdata.get('type')
                text = prereqdata.get('text')
                label = prereqdata.get('url_text')
                recommended = prereqdata.get('recommended')
                required = prereqdata.get('required')
                
                # Set category
                category = Prerequisite.EXTERNAL_LINK
                if type == 'workshop':
                    category = Prerequisite.WORKSHOP
                    linked_workshop = search(Workshop, prereqdata.get('potential_name'), log)
                    log.log(f'Success: Found a prerequired workshop for `{name}` in the database ({linked_workshop}).')
                elif type == 'software':
                    category = Prerequisite.SOFTWARE
                    linked_software = search(Software, prereqdata.get('potential_name'), log)
                    log.log(f'Success: Found a prerequired software for `{name}` in the database ({linked_software}).')
                elif type == 'insight':
                    category = Prerequisite.INSIGHT
                    linked_insight = search(Insight, prereqdata.get('potential_name'), log)
                    log.log(f'Success: Found a prerequired insight for `{name}` in the database ({linked_insight}).')
                
                if category == Prerequisite.EXTERNAL_LINK:
                    linked_external, created = URL.objects.get_or_create(url=url, label=label)
                
                prerequisite, created = Prerequisite.objects.update_or_create(
                    linked_workshop=linked_workshop,
                    linked_software=linked_software,
                    linked_insight=linked_insight,
                    linked_external=linked_external,
                    text=text,
                    category=category,
                    frontmatter=frontmatter,
                    recommended=recommended,
                    required=required
                )

        log.log(
            'Added/updated requirements for workshops: ' + ', '.join([x[0] for x in workshops]))

        if log._save(data='ingestprerequisites', name='warnings.md', warnings=True) or log._save(data='ingestprerequisites', name='logs.md', warnings=False, logs=True) or log._save(data='ingestprerequisites', name='info.md', warnings=False, logs=False, info=True):
            log.log(f'Log files with any warnings and logging information is now available in: `{log.LOG_DIR}`', force=True)