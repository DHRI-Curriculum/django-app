import os
from bs4 import BeautifulSoup
from django.core.management import BaseCommand
from django.conf import settings
from backend.dhri.log import Logger
from backend import dhri_settings
from backend.dhri.loader import Loader, process_links
from ._shared import get_name, LogSaver
import yaml
import pathlib


def check_for_cancel(SAVE_DIR, workshop):
    if pathlib.Path(SAVE_DIR).exists():
        _ = input(f'{workshop} already exists. Replace? [n/Y]')
        if _ == '' or _.lower() == 'y':
            pass
        else:
            exit('User exit.')


def process_prereq_text(html, log=None):
    soup = BeautifulSoup(html, 'lxml')
    text = ''
    captured_link = False
    warnings = []
    for text_node in soup.find_all(string=True):
        if text_node.parent.name.lower() == 'a' and not captured_link: # strip out the first link
            captured_link = text_node.parent['href']
            continue
        
        if text_node.parent.name.lower() == 'a':
            warnings.append(log.warning(f'Found more than one link in a prerequirement. The first link (`{captured_link}`) will be treated as the requirement, and any following links, such as `{text_node.parent["href"]}`, will be included in the accompanying text for the requirement.'))
            text += f'<a href="{text_node.parent["href"]}" target="_blank">' + text_node.strip().replace('(recommended) ', '').replace('(required) ', '') + '</a> '
        else:
            text += text_node.strip().replace('(recommended) ', '').replace('(required) ', '') + ' '

    text = text.strip()
    
    if text == '(required)':
        text = None

    if text == '(recommended)':
        text = None

    if text == '':
        text = None

    return text, warnings


class Command(LogSaver, BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from workshops in the GitHub repository (provided through --workshop parameter)'
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Automatically approves any requests to replace/update existing local data.')
        parser.add_argument('--forcedownload', action='store_true', help='Forces the script to re-load all the locally stored data, despite any settings made for expiry dates on caches.')
        parser.add_argument('--save_all', action='store_true')
        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument('--name', nargs='+', type=str, help='Provide a specific name of a workshop to build.')
        group.add_argument('--all', action='store_true', help='Build all workshop datafiles.')
        parser.add_argument('--silent', action='store_true', help='Makes as little output as possible, although still saves all the information in log files (see debugging docs).')
        parser.add_argument('--verbose', action='store_true', help='Provides all output possible, which can be overwhelming. Good for debug purposes, not for the faint of heart.')

    def handle(self, *args, **options):
        log = Logger(name=get_name(__file__), force_verbose=options.get('verbose'), force_silent=options.get('silent'))

        log.log('Building workshop files... Please be patient as this can take some time.')

        if options.get('all'):
            options['name'] = [x[0] for x in dhri_settings.AUTO_REPOS]

        if not options.get('name'):
            log.error(
                'No workshop names provided. Use any of the following settings:\n    --name [repository name]\n    --all')

        for workshop in options.get('name'):
            SAVE_DIR = f'{settings.BASE_DIR}/_preload/_workshops/{workshop}'
            DATA_FILE = f'{workshop}.yml'
            if not options.get('force'):
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

            l = Loader(url, branch, force_download=options.get('forcedownload'))
            
            # 1. Extract workshop data
            workshop = {
                'slug': slug,
                'name': l.title,
                'parent_backend': l.parent_backend,
                'parent_repo': l.parent_repo,
                'parent_branch': l.parent_branch,
                'image': l.image_path,
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
            
            for html in l.prerequisites:
                url_text, url = process_links(html, 'prerequisite', is_html=True)

                required, recommended = False, False
                if '(required)' in html:
                    required = True
                if '(recommended)' in html:
                    recommended = True

                if 'github.com/DHRI-Curriculum/install/' in url:
                    text, w = process_prereq_text(html, log)
                    self.WARNINGS.extend(w)
                    if not text:
                        self.WARNINGS.append(log.warning(f'No clarifying text was found when processing prerequired installation (`{url_text}`) for workshop `{workshop.get("name")}`. Note that the clarifying text will be replaced by the "why" text from the installation instructions. You may want to change this in the frontmatter\'s requirements for the workshop {workshop.get("name")} and re-run `buildworkshop --name {os.path.basename(DATA_FILE).replace(".md", "")}` or manually edit the data file: `{SAVE_DIR}/{DATA_FILE}`'))
                    data['frontmatter']['prerequisites'].append({'type': 'install', 'potential_name': url_text, 'potential_slug_fragment': url.split('/')[-1].replace('.md', ''), 'text': text, 'required': required, 'recommended': recommended})
                elif 'github.com/DHRI-Curriculum/insights/' in url:
                    text, w = process_prereq_text(html, log)
                    self.WARNINGS.extend(w)
                    if not text:
                        self.WARNINGS.append(log.warning(f'No clarifying text was found when processing prerequired insight (`{url_text}`) for workshop `{workshop.get("name")}`. Note that the clarifying text will be replaced by the text presenting the insight. You may want to change this in the frontmatter\'s requirements for the workshop {workshop.get("name")} and re-run `buildworkshop --name {os.path.basename(DATA_FILE).replace(".md", "")}` or manually edit the data file: `{SAVE_DIR}/{DATA_FILE}`'))
                    data['frontmatter']['prerequisites'].append({'type': 'insight', 'potential_name': url_text, 'potential_slug_fragment': url.split('/')[-1].replace('.md', ''), 'text': text, 'required': required, 'recommended': recommended})
                elif 'github.com/DHRI-Curriculum/' in url and not '/blob/' in url:
                    text, w = process_prereq_text(html, log)
                    self.WARNINGS.extend(w)
                    if not text:
                        self.WARNINGS.append(log.warning(f'No clarifying text was found when processing prerequired workshop (`{url_text}`) for workshop `{workshop.get("name")}`. Note that the clarifying text will not be replaced by any other text. You may want to change this in the frontmatter\'s requirements for the workshop {workshop.get("name")} and re-run `buildworkshop --name {os.path.basename(DATA_FILE).replace(".md", "")}` or manually edit the data file: `{SAVE_DIR}/{DATA_FILE}`'))
                    data['frontmatter']['prerequisites'].append({'type': 'workshop', 'potential_name': url_text, 'text': text, 'required': required, 'recommended': recommended})
                else:
                    text = html
                    if not text:
                        self.WARNINGS.append(log.warning(f'No accompanying text was found when processing prerequired external link (`{url}`) for workshop `{workshop.get("name")}`. Note that the clarifying text will not be replaced by any other text. You may want to change this in the frontmatter\'s requirements for the workshop {workshop.get("name")} and re-run `buildworkshop --name {os.path.basename(DATA_FILE).replace(".md", "")}` or manually edit the data file: `{SAVE_DIR}/{DATA_FILE}`'))
                    data['frontmatter']['prerequisites'].append({'type': 'external link', 'url': url, 'text': text, 'required': required, 'recommended': recommended})

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
                        self.WARNINGS.append(log.warning('could not find current, original, or past in role',
                              low_role, '--setting automatically to past.'))

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

            self.LOGS.append(log.log(f'Saved workshop datafile: `{SAVE_DIR}/{DATA_FILE}`'))

            self.SAVE_DIR = self.SAVE_DIR = f'{LogSaver.LOG_DIR}/buildworkshop/{workshop.get("slug")}'
            if self._save(data=workshop, name='warnings.md', warnings=True) or self._save(data=workshop, name='logs.md', warnings=False, logs=True):
                log.log('Log files with any warnings and logging information is now available in the' + self.SAVE_DIR, force=True)
