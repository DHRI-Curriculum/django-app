from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger
from backend import dhri_settings
from backend.dhri.loader import Loader, process_links
from ._shared import get_name
import yaml
import pathlib


def check_for_cancel(SAVE_DIR, workshop):
    if pathlib.Path(SAVE_DIR).exists():
        _ = input(f'{workshop} already exists. Replace? [n/Y]')
        if _ == '' or _.lower() == 'y':
            pass
        else:
            exit('User exit.')


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from workshops in the GitHub repository (provided through --workshop parameter)'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true')
        parser.add_argument('--force', action='store_true')
        parser.add_argument('--save_all', action='store_true')
        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument('--name', nargs='+', type=str)
        group.add_argument('--all', action='store_true')
        parser.add_argument('--silent', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        log = Logger(name=get_name(__file__), force_verbose=options.get('verbose'), force_silent=options.get('silent'))

        if options.get('all') or options.get('reset'):
            options['name'] = [x[0] for x in dhri_settings.AUTO_REPOS]

        if not options.get('name'):
            log.error(
                'No workshop names provided. Use any of the following settings:\n    --name [repository name]\n    --all')

        for workshop in options.get('name'):
            SAVE_DIR = f'{settings.BASE_DIR}/_preload/_workshops/{workshop}'
            DATA_FILE = f'{workshop}.yml'
            if not options.get('force') and not options.get('reset'):
                check_for_cancel(SAVE_DIR, workshop)

            if not pathlib.Path(SAVE_DIR).exists():
                pathlib.Path(SAVE_DIR).mkdir(parents=True)

            # Start processing...
            data = {
                'workshop': {},
                'frontmatter': {},
                'praxis': {},
                'lessons': []
            }
            slug = workshop
            url = f'https://github.com/DHRI-Curriculum/{workshop}'
            branch = 'v2.0'

            # TODO: force_download doesn't seem to work here.
            l = Loader(url, branch, force_download=options.get('force'))

            # 1. Extract workshop data
            workshop = {
                'slug': slug,
                'name': l.title,
                'parent_backend': l.parent_backend,
                'parent_repo': l.parent_repo,
                'parent_branch': l.parent_branch
            }
            data['workshop'] = workshop

            if options.get('save_all'):
                with open(f'{SAVE_DIR}/workshop.yml', 'w+') as file:
                    file.write(yaml.dump(workshop))

            # 2. Extract frontmatter
            data['frontmatter'] = {
                'abstract': l.abstract,
                'estimated_time': l.frontmatter['estimated_time'],
                'ethical_considerations': l.ethical_considerations,
                'learning_objectives': l.learning_objectives,
                'projects': [],
                'readings': [],
                'contributors': [],
                'prerequisites': [],
                'resources': []
            }

            for annotation in l.projects:
                p_title, url = process_links(annotation, 'project')
                data['frontmatter']['projects'].append({
                    'annotation': annotation,
                    'title': p_title,
                    'url': url
                })

            for annotation in l.readings:
                r_title, url = process_links(annotation, 'reading')
                data['frontmatter']['readings'].append({
                    'annotation': annotation,
                    'title': r_title,
                    'url': url
                })
            
            for prereq in l.prerequisites:
                p_title, url = process_links(prereq, 'prerequisite')

                required, recommended = False, False
                if '(required)' in prereq:
                    required = True
                if '(recommended)' in prereq:
                    recommended = True

                if 'github.com/DHRI-Curriculum/install/' in url:
                    data['frontmatter']['prerequisites'].append({'type': 'install', 'potential_software': p_title, 'potential_slug_fragment': url.split('/')[-1].replace('.md', ''), 'full_text': prereq, 'required': required, 'recommended': recommended})
                elif 'github.com/DHRI-Curriculum/' in url and not '/blob/' in url:
                    data['frontmatter']['prerequisites'].append({'type': 'workshop', 'potential_name': p_title, 'full_text': prereq, 'required': required, 'recommended': recommended})
                else:
                    data['frontmatter']['prerequisites'].append({'type': 'external link', 'url': url, 'full_text': prereq, 'required': required, 'recommended': recommended})

            for resourcedata in l.resources:
                r_title, url = process_links(resourcedata, 'resource')
                if 'https://raw.githubusercontent.com/DHRI-Curriculum/' in url or ('github.com/DHRI-Curriculum/' and '/raw/' in url):
                    data['frontmatter']['resources'].append({'type': 'internal_download', 'url': url, 'title': r_title, 'full_text': resourcedata})
                else:
                    data['frontmatter']['resources'].append({'type': 'external_link', 'url': url, 'title': r_title, 'full_text': resourcedata})
                
            for contributor in l.contributors:
                role = ''
                is_current = False

                if contributor.get('role'):
                    low_role = contributor.get('role').lower()
                    if 'author' in low_role or 'contributor' in low_role:
                        role = 'Au'
                    if 'review' in low_role:
                        role = 'Re'
                    if 'editor' in low_role:
                        role = 'Ed'
                    is_current = 'current' in low_role
                    is_past = 'original' in low_role or 'past' in low_role

                    if not is_current and not is_past:
                        log.warning('could not find current, original, or past in role',
                              low_role, '--setting automatically to past.')

                contributor_data = {
                    'first_name': contributor.get('first_name'),
                    'last_name': contributor.get('last_name'),
                    'url': contributor.get('url'),
                    'collaboration': {
                        'workshop': slug,
                        'role': role,
                        'current': is_current
                    }
                }

                data['frontmatter']['contributors'].append(contributor_data)

            if options.get('save_all'):
                with open(f'{SAVE_DIR}/frontmatter.yml', 'w+') as file:
                    file.write(yaml.dump(data['frontmatter']))

            # 3. Extract praxis

            data['praxis'] = {
                'workshop': slug,
                'intro': l.praxis_intro,
                'tutorials': [],
                'further_readings': [],
                'further_projects': [],
                'more_resources': [],
                'discussion_questions': [],
                'next_steps': []
            }

            for annotation in l.tutorials:
                label, url = process_links(annotation, 'tutorial')
                data['praxis']['tutorials'].append({
                    'annotation': annotation,
                    'label': label,
                    'url': url
                })

            for annotation in l.further_readings:
                r_title, url = process_links(annotation, 'reading')
                data['praxis']['further_readings'].append({
                    'annotation': annotation,
                    'title': r_title,
                    'url': url
                })
            
            for annotation in l.further_projects:
                p_title, url = process_links(annotation, 'reading')
                data['praxis']['further_projects'].append({
                    'annotation': annotation,
                    'title': p_title,
                    'url': url
                })
            
            for annotation in l.more_resources:
                p_title, url = process_links(annotation, 'project')
                data['praxis']['more_resources'].append({
                    'annotation': annotation,
                    'title': p_title,
                    'url': url
                })

            for order, label in enumerate(l.discussion_questions, start=1):
                data['praxis']['discussion_questions'].append({
                    'workshop': slug,
                    'label': label,
                    'order': order
                })

            for order, label in enumerate(l.next_steps, start=1):
                data['praxis']['next_steps'].append({
                    'workshop': slug,
                    'label': label,
                    'order': order
                })

            if options.get('save_all'):
                with open(f'{SAVE_DIR}/praxis.yml', 'w+') as file:
                    file.write(yaml.dump(data['praxis']))

            # 4. Extract lessons
            lessons = list()

            for order, lesson_data in enumerate(l.as_html.lessons, start=1):
                lesson = {
                    'workshop': slug,
                    'title': lesson_data.get('title', ''),
                    'text': '\n'.join([x for x in lesson_data.get('text', '').strip().splitlines() if x]),
                    'order': order,
                    'challenge': '',
                    'challenge_title': lesson_data.get('challenge_title', ''),
                    'solution': '',
                    'solution_title': lesson_data.get('solution_title', ''),
                    'questions': [],
                    'keywords': []
                }

                # Extract challenges
                if lesson_data['challenge']:
                    lesson['challenge'] = '\n'.join(
                        [x for x in lesson_data['challenge'].strip().splitlines() if x])

                    if lesson_data['solution']:
                        lesson['solution'] = '\n'.join(
                            [x for x in lesson_data['solution'].strip().splitlines() if x])

                for d in lesson_data.get('evaluation', []):
                    if d.get('question'):
                        question = d['question']

                        lesson['questions'].append({
                            'question': question,
                            'answers': d.get('answers')
                        })

                if lesson_data.get('keywords'):
                    lesson['keywords'] = [x['title']
                                          for x in lesson_data['keywords']]

                lessons.append(lesson)

            data['lessons'] = lessons

            if options.get('save_all'):
                with open(f'{SAVE_DIR}/lessons.yml', 'w+') as file:
                    file.write(yaml.dump(lessons))

            # Save all data
            with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
                file.write(yaml.dump(data))
