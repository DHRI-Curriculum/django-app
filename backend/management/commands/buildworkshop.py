from backend.github import WorkshopCache
from bs4 import BeautifulSoup
from django.core.management import BaseCommand
from django.conf import settings
from backend.logger import Logger
from backend import settings

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
        if text_node.parent.name.lower() == 'a' and not captured_link:  # strip out the first link
            captured_link = text_node.parent['href']
            continue

        if text_node.parent.name.lower() == 'a':
            warnings.append(log.warning(
                f'Found more than one link in a prerequirement. The first link (`{captured_link}`) will be treated as the requirement, and any following links, such as `{text_node.parent["href"]}`, will be included in the accompanying text for the requirement.'))
            text += f'<a href="{text_node.parent["href"]}" target="_blank">' + text_node.strip(
            ).replace('(recommended) ', '').replace('(required) ', '') + '</a> '
        elif text_node.parent.name.lower() == 'p':
            text += text_node.strip().replace('(recommended) ', '').replace('(required) ', '')
        elif not text_node.parent.attrs and not text_node.parent.is_empty_element:
            text += f' <{text_node.parent.name}>{text_node}</{text_node.parent.name}> '
        else:
            log.error(f'The prerequirement contains a HTML tag ({text_node.parent.name}) that cannot be processed. They need to be added to the process_prereq_text function. If you do not know how to do this, try reformulating the provided HTML to only include <a>, <p>, or any _not self-closing tags_ with _no attributes_ (i.e. `<code>...</code>`, `<i>...</i>`, etc.) on the top level of your HTML:' + html, raise_error=NotImplementedError)

    text = text.strip()

    if text == '(required)':
        text = None

    if text == '(recommended)':
        text = None

    if text == '':
        text = None

    return text, warnings


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Build YAML files from workshops in the GitHub repository (provided through --workshop parameter)'
    SAVE_DIR = ''
    WARNINGS, LOGS = [], []

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Automatically approves any requests to replace/update existing local data.')
        parser.add_argument('--forcedownload', action='store_true',
                            help='Forces the script to re-load all the locally stored data, despite any settings made for expiry dates on caches.')
        parser.add_argument('--save_all', action='store_true')
        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument('--name', nargs='+', type=str,
                           help='Provide a specific name of a workshop to build.')
        group.add_argument('--all', action='store_true',
                           help='Build all workshop datafiles.')
        parser.add_argument('--silent', action='store_true',
                            help='Makes as little output as possible, although still saves all the information in log files (see debugging docs).')
        parser.add_argument('--verbose', action='store_true',
                            help='Provides all output possible, which can be overwhelming. Good for debug purposes, not for the faint of heart.')

    def handle(self, *args, **options):
        log = Logger(path=__file__,
            force_verbose=options.get('verbose'),
            force_silent=options.get('silent')
        )

        if options.get('all'):
            options['name'] = [x[0] for x in settings.AUTO_REPOS]

        if not options.get('name'):
            log.error(
                'No workshop names provided. Use any of the following settings:\n    --name [repository name]\n    --all')

        log.log(
            'Building workshop files... Please be patient as this can take some time.')

        for workshop in options.get('name'):
            SAVE_DIR = f'{settings.BASE_DIR}/_preload/_workshops/{workshop}'
            DATA_FILE = f'{workshop}.yml'
            if not options.get('force'):
                check_for_cancel(SAVE_DIR, workshop)

            if not pathlib.Path(SAVE_DIR).exists():
                pathlib.Path(SAVE_DIR).mkdir(parents=True)

            loader = WorkshopCache(workshop, log=log)
            data = loader.data

            # Save all data
            with open(f'{SAVE_DIR}/{DATA_FILE}', 'w+') as file:
                file.write(yaml.dump(data))

                log.log(f'Saved workshop datafile: `{SAVE_DIR}/{DATA_FILE}`')

            if log._save(data=workshop, name='warnings.md', warnings=True) or log._save(data=workshop, name='logs.md', warnings=False, logs=True):
                log.log(
                    'Log files with any warnings and logging information is now available in the' + log.LOG_DIR, force=True)
