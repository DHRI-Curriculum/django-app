from backend.dhri_utils import get_verbose
from django.conf import settings
from django.utils.termcolors import colorize
from colorama import Style

import datetime
import textwrap
import pathlib
import progressbar

from backend.dhri_utils import get_verbose, get_terminal_width

COLON_SAFE = {
    'http://': 'HTTP///',
    'https://': 'HTTPS///',
    'ftp://': 'FTP///',
    'mailto:': 'MAILTO///',
}


def _get_parts_of_log_message(message):
    for search, replace in COLON_SAFE.items():
        message = message.replace(search, replace)
    is_multiline = False
    lines = message.split('\n')
    main_message, following_lines = '', []
    if len(lines) > 1:
        is_multiline = True
    if is_multiline:
        # multiline message
        line1 = lines[0]
        finder = line1.split(':')
        if (('warning:' in line1.lower() or 'error:' in line1.lower()) and len(finder) >= 3) or len(finder) >= 2:
            # we have at least one colon in the message, so we want to split off the last part and make that into the first of the following lines...
            main_message = ':'.join(line1.split(':')[:-1])
            lines[0] = line1.split(':')[-1].strip()
            following_lines = [x.strip() for x in lines if x.strip()]
    else:
        # single line message
        if (('warning:' in message.lower() or 'error:' in message.lower()) and len(message.split(':')) >= 3) or len(message.split(':')) >= 3:
            finder = message.split(':')
            main_message = ':'.join(message.split(':')[:-1])
            lines[0] = message.split(':')[-1].strip()
            following_lines = [x.strip() for x in lines if x.strip()]
        elif len(message.split(':')) == 2:
            if 'warning' in message.lower() or 'error' in message.lower():
                main_message = message
                following_lines = []
            else:
                # no warning/error
                main_message = message.split(':')[0]
                following_lines = [message.split(':')[1].strip()]
        else:  # ===    elif len(message.split(':')) >= 1:    ===     we have a simple message with no : in it
            main_message = message
    for search, replace in COLON_SAFE.items():
        main_message = main_message.replace(replace, search)
        following_lines = [x.replace(replace, search) for x in following_lines]
    return(main_message, following_lines)


def _fix_message(main_message='', following_lines=[], first_line_add='--> ', indentation='    ', first_line_bold=True):
    if not following_lines:
        main_message, following_lines = _get_parts_of_log_message(
            main_message)  # try

    if following_lines:
        main_message += ':'

    # Fix terminal width
    if len(first_line_add) >= len(indentation):
        width = get_terminal_width() - len(first_line_add)
    else:
        width = get_terminal_width() - len(indentation)

    dedented_text = textwrap.dedent(main_message)
    wrapped = textwrap.fill(dedented_text, width=width)
    message = textwrap.indent(wrapped, indentation)
    if first_line_bold == True:
        output = colorize(first_line_add + message.strip(), opts=('bold',))
    else:
        output = first_line_add + message.strip()

    if following_lines:
        dedented_text = textwrap.dedent('\n'.join(following_lines))
        following_lines = [textwrap.fill(x, width=width)
                           for x in following_lines]
        wrapped = '\n'.join(following_lines)
        quote = textwrap.indent(wrapped, indentation)
        output += "\n" + quote

    return(output)

class Logger():

    INFOS = []
    WARNINGS = []
    LOGS = []

    progressbar.streams.wrap_stderr()
    BAR = progressbar.ProgressBar(max_value=progressbar.UnknownLength, redirect_stdout=True)

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', '')
        self.path = kwargs.get('path', '')

        if self.path:
            self.name = self.path.split('/')[-1].replace('.py', '')

        self.LOG_DIR = f'{settings.BASE_DIR}/_logs/{self.name}'

        self.force_verbose = False
        self.force_silent = False

        if ('force_verbose' in kwargs and kwargs['force_verbose']) and ('force_silent' in kwargs and kwargs['force_silent']):
            exit('Logger can only accept either force_verbose OR force_silent, not both simultaneously.')

        self.VERBOSE = get_verbose()

        if kwargs.get('force_verbose'):
            self.VERBOSE = True

        if kwargs.get('force_silent'):
            self.VERBOSE = False

    def log(self, main_message="", color='green', force=False):
        self.LOGS.append((self.get_timestamp(), main_message))
        message = self._fix_message(main_message)
        message = colorize(message, fg=color, opts=('',))
        if self.VERBOSE or force == True:
            self.output(message)
        return main_message

    def info(self, main_message="", color='cyan', force=False):
        self.INFOS.append((self.get_timestamp(), main_message))
        message = self._fix_message(main_message)
        message = colorize(message, fg=color, opts=('',))
        if self.VERBOSE or force == True:
            self.output(message)
        return main_message

    def error(self, main_message="", raise_error=None, kill=True, color='red'):
        if raise_error:
            raise(raise_error('Error: ' + main_message)) from None
        message = self._fix_message('Error: ' + main_message)
        message = colorize(message, fg=color, opts=('bold',))
        self.output(message, kill)
        return main_message

    def warning(self, main_message="", kill=False, color='yellow'):
        self.WARNINGS.append((self.get_timestamp(), main_message))
        message = self._fix_message('Warning: ' + main_message)
        message = colorize(message, fg=color, opts=('bold',))
        self.output(message, kill)
        return main_message

    def output(self, message: str, kill=False):
        message = Style.DIM + f"[{self.name}] " + Style.RESET_ALL + message
        if kill == True:
            exit(message)
        else:
            print(message)

    def _save(self, lst=[], data={}, name='log.md', warnings=True, logs=False, info=False, step='buildworkshop'):
        ''' Private function to save a list of warnings and logs'''

        if not lst and not warnings and not logs and not info:
            return False
        elif not lst and warnings:
            lst = self.WARNINGS
        elif not lst and logs:
            lst = self.LOGS
        elif not lst and info:
            lst = self.INFOS

        if not lst:
            return False

        if not pathlib.Path(self.LOG_DIR).exists():
            pathlib.Path(self.LOG_DIR).mkdir(parents=True)

        with open(f'{self.LOG_DIR}/{name}', 'w+') as f:
            if type(data) == dict and data.get("name"):
                f.write('# Workshop: [' + data.get("name") + '](https://www.github.com/' + data.get(
                    'parent_repo') + '/tree/' + data.get('parent_branch') + ')\n\n')
            elif type(data == str):
                f.write(f'# {data}\n\n')
            f.write(f'**Log file created:** {self.get_timestamp()}\n\n')
            if warnings:
                f.write('## Warnings:\n\n')
            elif logs:
                f.write('## Logs:\n\n')
            elif info:
                f.write('## Information:\n\n')
            else:
                f.write('## List:\n\n')
            for datapoint in lst:
                f.write('[ ] ' + datapoint[0] + ' -- ' + datapoint[1] + '\n')
            f.write(f'\n\n---\n\nWarnings do not need to be resolved in order for the data to be correctly ingested but there may be issues that you want to resolve.\n\n')
            if step == 'buildworkshop' and type(data) == dict and data.get("name") and data.get("slug"):
                f.write(
                    f'If you have finished resolving the warnings above (or if you do not wish to resolve the warnings), rerun the `buildworkshop` command, and then proceed with the ingestion of the workshop. You ingest the workshop by running either of the following two commands:\n- `python manage.py ingestworkshop --name {data.get("slug")}`\n- `python manage.py ingestworkshop --all`\n\nAdd the `--forceupdate` flag to any of them if you do not want to confirm all edits.')

        return True

    def _fix_message(self, main_message='', following_lines=[], first_line_add='', indentation='    ', first_line_bold=True):
        # +3 because name is put in brackets and a space is added
        indentation = (len(self.name) + 3) * ' '
        return(_fix_message(main_message=main_message, following_lines=[], first_line_add='', indentation=indentation, first_line_bold=True))

    def get_timestamp(self):
        return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')


def get_or_default(message: str, default_variable: str, color='blue', evaluate=str) -> str:
    inp = Input('')
    _ = inp.ask(f'{message} [default "{default_variable}"]: ', color=color)
    if _ != '':
        try:
            return(evaluate(_))
        except:
            return(_)
    else:
        try:
            return(evaluate(default_variable))
        except:
            return(_)


class Input:

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', '')
        self.path = kwargs.get('path', '')

        if self.path:
            self.name = self.path.split('/')[-1].replace('.py', '')

    def ask(self, question='', bold=True, color='yellow', start_with_newline=True):
        # +3 because name is put in brackets and a space is added
        indentation = (len(self.name) + 3) * ' '
        message = _fix_message(main_message=question,
                               first_line_add='', indentation='') + ' '
        opts = ('',)
        if bold == True:
            opts = ('bold',)
        message = colorize(message, fg=color, opts=opts)
        if start_with_newline:
            message = "\n" + message
        return(input(message+"\n"))
