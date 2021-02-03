from workshop.models import Prerequisite, PrerequisiteSoftware, Workshop, Frontmatter
from insight.models import Insight
from install.models import Software
from django.core.management import BaseCommand
from backend.dhri.log import Logger, Input
from backend.mixins import convert_html_quotes
from ._shared import get_yaml, get_name, get_all_existing_workshops, LogSaver


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
    if [x for x in finders if x.count() > 0] and [x for x in finders if x.count() == 1]: # we have at least one workshop that matches the searches above
        linked_workshop = [x for x in finders if x.count() == 1][0][0]
        return linked_workshop
    elif [x for x in finders if x.count() > 0]:
        log.error(f'There are multiple workshops in the database that match the linked workshop in the prerequisite for {for_workshop}. Please disambiguate by adjusting the repository or the local datafile ({DATAFILE}), and after that, rerun python manage.py ingestworkshop --name {for_workshop} followed by python manage.py ingestprerequisites. The following searches were conducted: {searches}')
        return False

    log.error(f'Unable to find workshops matching the linked workshop in the prerequisite for {for_workshop}. Please check for misspelling or adjust the repository or the local datafile ({DATAFILE}). After that, rerun python manage.py ingestworkshop --name {for_workshop} followed by python manage.py ingestprerequisites. The following searches were conducted: {searches}')
    return False


def get_fragments_of_name(name):
    if len(name) > 30:
        return [
            ''.join(name[:10]),
            ''.join(name[-10:]),
        ]
    return []


def search_install(potential_name, for_workshop=None, log=None, DATAFILE=None):
    potential_name = potential_name.lower()
    searches = [
        potential_name,
        potential_name.replace('installing', ''),
        potential_name.replace('install', ''),
    ]
    searches.extend(get_fragments_of_name(potential_name))
    finders = [Software.objects.filter(software__icontains=x) for x in searches]
    if [x for x in finders if x.count() > 0]: 
        if [x for x in finders if x.count() >= 1]: # we have at least one software installation that matches the searches above
            linked_installs = [x for x in finders if x.count() >= 1][0]
            return linked_installs
    log.error(f'Unable to find installation instructions matching the linked workshop in the prerequisite for {for_workshop}. Please check for misspelling or adjust the repository or the local datafile ({DATAFILE}). After that, rerun python manage.py ingestworkshop --name {for_workshop} followed by python manage.py ingestprerequisites. The following searches were conducted: {searches}')
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
        if [x for x in finders if x.count() > 0] and [x for x in finders if x.count() == 1]: # we have at least one insight that matches the searches above
            linked_insight = [x for x in finders if x.count() == 1][0][0]
            return linked_insight
        elif [x for x in finders if x.count() > 0]:
            log.error(f'There are multiple insights in the database that match the linked insight in the prerequisite for {for_workshop}. Please disambiguate by adjusting the repository or the local datafile ({DATAFILE}), and after that, rerun python manage.py ingestworkshop --name {for_workshop} followed by python manage.py ingestprerequisites. The following searches were conducted: {searches}')
            return False

    else:
        searches = [potential_slug_fragment]
        finders = [Insight.objects.filter(slug__icontains=potential_slug_fragment) for x in searches]
        if [x for x in finders if x.count() > 0]: 
            if [x for x in finders if x.count() > 0] and [x for x in finders if x.count() == 1]: # we have at least one insight that matches the searches above
                linked_insight = [x for x in finders if x.count() == 1][0][0]
                return linked_insight
            elif [x for x in finders if x.count() > 0]:
                log.error(f'There are multiple insights in the database that match the linked insight in the prerequisite for {for_workshop}. Please disambiguate by adjusting the repository or the local datafile ({DATAFILE}), and after that, rerun python manage.py ingestworkshop --name {for_workshop} followed by python manage.py ingestprerequisites. The following searches were conducted: {searches}')
                return False

    log.error(f'Unable to find insights matching the linked insight in the prerequisite for {for_workshop}. Please check for misspelling or adjust the repository or the local datafile ({DATAFILE}). After that, rerun python manage.py ingestworkshop --name {for_workshop} followed by python manage.py ingestprerequisites. The following searches were conducted: {searches}')
    return False


class Command(LogSaver, BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Ingests internal DHRI YAML files with information about all the existing workshops into the database'
    requires_migrations_checks = True
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--forceupdate', action='store_true')
        parser.add_argument('--name', nargs='+', type=str)
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(name=get_name(__file__), force_verbose=options.get('verbose'), force_silent=options.get('silent'))
        input = Input(name=get_name(__file__))

        workshops = get_all_existing_workshops()
        
        if options.get('name'):
            workshops = get_all_existing_workshops(options.get('name'))

        for _ in workshops:
            name, path = _
            workshop, frontmatter = None, None
            DATAFILE = f'{path}/{name}.yml'
            
            superdata = get_yaml(DATAFILE)

            # Separate out data
            frontmatterdata = superdata.get('frontmatter')
            workshopdata = superdata.get('workshop')
            
            # 1. FIND WORKSHOP
            try:
                workshop = Workshop.objects.get(name = workshopdata.get('name'))
            except:
                log.error(f'The workshop `{workshopdata.get("name")}` could not be found. Make sure you ran python manage.py ingestworkshop --name {workshopdata.get("name")} before running this command.')

            # 2. FIND FRONTMATTER
            try:
                frontmatter = Frontmatter.objects.get(workshop=workshop)
            except:
                log.error(f'Frontmatter for the workshop `{workshopdata.get("name")}` could not be found. Make sure you ran python manage.py ingestworkshop --name {workshopdata.get("name")} before running this command.')

            for prereqdata in frontmatterdata.get('prerequisites'):
                linked_workshop, linked_installs, linked_insight = None, None, None
                url = prereqdata.get('url')
                category = Prerequisite.EXTERNAL_LINK

                if prereqdata.get('type') == 'workshop':
                    linked_workshop = search_workshop(prereqdata.get('potential_name'), workshopdata.get("name"), log, DATAFILE)
                    q = f'Prerequisite workshop `{linked_workshop.name}`'
                    category = Prerequisite.WORKSHOP
                    self.LOGS.append(log.log(f'Linking workshop prerequisite for `{workshopdata.get("name")}`: {linked_workshop.name}'))
                elif prereqdata.get('type') == 'install':
                    linked_installs = search_install(prereqdata.get('potential_name'), workshopdata.get("name"), log, DATAFILE) # currently, not using prereqdata.get('potential_slug_fragment') - might be something we want to do in the future
                    q = f'Prerequisite installations ' + ', '.join([f'`{x.software}`' for x in linked_installs])
                    category = Prerequisite.INSTALL
                    self.LOGS.append(log.log(f'Linking installation prerequisite for `{workshopdata.get("name")}`: {[x.software for x in linked_installs]}'))
                elif prereqdata.get('type') == 'insight':
                    linked_insight = search_insight(prereqdata.get('potential_name'), prereqdata.get('potential_slug_fragment'), workshopdata.get("name"), log, DATAFILE)
                    q = f'Prerequisite insight `{linked_insight.title}`'
                    category = Prerequisite.INSIGHT
                    self.LOGS.append(log.log(f'Linking insight prerequisite for `{workshopdata.get("name")}`: {linked_insight.title}'))

                prerequisite, created = Prerequisite.objects.get_or_create(category=category, linked_workshop=linked_workshop, linked_insight=linked_insight, url=url, text=convert_html_quotes(prereqdata.get('text', '')), required=prereqdata.get('required'), recommended=prereqdata.get('recommended'))

                if linked_installs:
                    for software in linked_installs:
                        through = PrerequisiteSoftware(prerequisite=prerequisite, software=software, required=prereqdata.get('required'), recommended=prereqdata.get('recommended'))
                        through.save()

                frontmatter.prerequisites.add(prerequisite)
                
        self.LOGS.append(log.log('Added/updated requirements for workshops: ' + ', '.join([x[0] for x in workshops])))

        self.SAVE_DIR = self.SAVE_DIR = f'{LogSaver.LOG_DIR}/ingestprerequisites'
        if self._save(data='ingestprerequisites', name='warnings.md', warnings=True) or self._save(data='ingestprerequisites', name='logs.md', warnings=False, logs=True):
            log.log('Log files with any warnings and logging information is now available in the' + self.SAVE_DIR, force=True)
