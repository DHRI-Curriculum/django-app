from django.utils.termcolors import colorize
from colorama import Fore, Back, Style

import textwrap

from backend.dhri_settings import VERBOSE, TERMINAL_WIDTH, saved_prefix


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
        else: # ===    elif len(message.split(':')) >= 1:    ===     we have a simple message with no : in it
            main_message = message
    for search, replace in COLON_SAFE.items():
        main_message = main_message.replace(replace, search)
        following_lines = [x.replace(replace, search) for x in following_lines]
    return(main_message, following_lines)


def _fix_message(main_message='', following_lines=[], first_line_add='--> ', indentation='    ', first_line_bold=True):
    if not following_lines:
        main_message, following_lines = _get_parts_of_log_message(main_message) # try
    
    if following_lines: main_message += ':'

    # Fix terminal width
    if len(first_line_add) >= len(indentation):
        width = TERMINAL_WIDTH - len(first_line_add)
    else:
        width = TERMINAL_WIDTH - len(indentation)

    dedented_text = textwrap.dedent(main_message)
    wrapped = textwrap.fill(dedented_text, width=width)
    message = textwrap.indent(wrapped, indentation)
    if first_line_bold == True:
        output = colorize(first_line_add + message.strip(), opts=('bold',))
    else:
        output = first_line_add + message.strip()

    if following_lines:
        dedented_text = textwrap.dedent('\n'.join(following_lines))
        following_lines = [textwrap.fill(x, width=width) for x in following_lines]
        # wrapped = textwrap.fill(dedented_text, width=width)
        wrapped = '\n'.join(following_lines)
        quote = textwrap.indent(wrapped, indentation)
        output += "\n" + quote

    return(output)


def log_created(created:bool, model='', preview='', id='', log=None):
    if not log:
        from backend.dhri.log import Logger
        log = Logger(name='created')
    if created:
        from backend.dhri_settings import saved_prefix
        log.log(saved_prefix + f'{model} `{preview}` added (ID {id}).')
    else:
        log.warning(f'{model} `{preview}` was not saved as it already exists (ID {id}).', color='green') # Set to green to not alarm


class Logger():
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', '')
        self.force_verbose = False
        self.force_silent = False
        
        if ('force_verbose' in kwargs and kwargs['force_verbose']) and ('force_silent' in kwargs and kwargs['force_silent']):
            exit('Logger can only accept either force_verbose OR force_silent, not both simultaneously.')

        self.VERBOSE = VERBOSE

        if kwargs.get('force_verbose'):
            self.VERBOSE = True

        if kwargs.get('force_silent'):
            self.VERBOSE = False

    def info(self, main_message="", color='cyan', force=False):
        message = self._fix_message(main_message)
        message = colorize(message, fg=color, opts=('',))
        if self.VERBOSE or force == True: self.output(message)
        return main_message

    def log(self, main_message="", color='green', force=False):
        message = self._fix_message(main_message)
        message = colorize(message, fg=color, opts=('',))
        if self.VERBOSE or force == True: self.output(message)
        return main_message

    def error(self, main_message="", raise_error=None, kill=True, color='red'):
        if raise_error:
            raise(raise_error('Error: ' + main_message)) from None
        message = self._fix_message('Error: ' + main_message)
        message = colorize(message, fg=color, opts=('bold',))
        self.output(message, kill)
        return main_message

    def warning(self, main_message="", kill=False, color='yellow'):
        message = self._fix_message('Warning: ' + main_message)
        message = colorize(message, fg=color, opts=('bold',))
        self.output(message, kill)
        return main_message

    def output(self, message:str, kill=False):
        message = Style.DIM + f"[{self.name}] " + Style.RESET_ALL + message
        if kill == True:
            exit(message)
        else:
            print(message)

    def _fix_message(self, main_message='', following_lines=[], first_line_add='', indentation='    ', first_line_bold=True):
        indentation = (len(self.name) + 3) * ' ' # +3 because name is put in brackets and a space is added
        return(_fix_message(main_message=main_message, following_lines=[], first_line_add='', indentation=indentation, first_line_bold=True))

    def created(self, created:bool, model='', preview='', id='', force=False, warning_color='yellow'):
        if created:
            self.log(saved_prefix + f'{model} `{preview}` added (ID {id}).', force=force)
        else:
            self.warning(f'{model} `{preview}` was not saved as it already exists (ID {id}).', color=warning_color)



class Input:

    def __init__(self, *args, **kwargs):
        self.name = ''
        if 'name' in kwargs:
            self.name = kwargs['name']

    def ask(self, question='', bold=True, color='yellow', start_with_newline=True):
        indentation = (len(self.name) + 3) * ' ' # +3 because name is put in brackets and a space is added
        message = _fix_message(main_message=question, first_line_add='', indentation='') + ' '
        opts = ('',)
        if bold == True:
            opts = ('bold',)
        message = colorize(message, fg=color, opts=opts)
        if start_with_newline: message = "\n" + message
        return(input(message+"\n"))


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
