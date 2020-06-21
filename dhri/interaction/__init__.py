from django.utils.termcolors import colorize
from dhri.settings import VERBOSE
from colorama import Fore, Back, Style

import textwrap, re, os

def _get_parts_of_log_message(message):
    g = re.search(r'(.*)\:\s(.*)', message)
    if not g:
        return((message, ''))
    else:
        return((g.groups()[0], g.groups()[1]))


def _fix_message(message='', quote='', first_line_add='--> ', indentation='    ', first_line_bold=True):
    from dhri.constants import TERMINAL_WIDTH
    if quote == '':
        message, quote = _get_parts_of_log_message(message) # try

    if quote != '': message += ':'
    dedented_text = textwrap.dedent(message)
    wrapped = textwrap.fill(dedented_text, width=TERMINAL_WIDTH-4)
    message = textwrap.indent(wrapped, indentation)
    if first_line_bold == True:
        output = colorize(first_line_add + message.strip(), opts=('bold',))
    else:
        output = first_line_add + message.strip()

    if quote != '':
        dedented_text = textwrap.dedent(quote)
        wrapped = textwrap.fill(dedented_text, width=TERMINAL_WIDTH-4)
        quote = textwrap.indent(wrapped, indentation)
        output += "\n" + quote

    return(output)


class Logger():
    def __init__(self, *args, **kwargs):
        self.name = ''
        if 'name' in kwargs:
            self.name = kwargs['name']

    def log(self, message="", kill=False, color='green'):
        message = self._fix_message(message)
        message = colorize(message, fg=color, opts=('',))
        self.output(message)

    def error(self, message="", raise_error=None, kill=True, color='red'):
        if raise_error != None:
            raise(raise_error(message))
        message = colorize('Error: ' + message, fg=color, opts=('bold',))
        self.output(message, kill)

    def warning(self, message="", kill=False, color='yellow'):
        message = self._fix_message(message)
        message = colorize('Warning: ' + message, fg=color, opts=('bold',))
        self.output(message, kill)

    def output(self, message:str, kill=False):
        if VERBOSE:
            message = Style.DIM + f"[{self.name}] " + Style.RESET_ALL + message
        if kill == True:
            exit(message)
        else:
            print(message)

    def _fix_message(self, message='', quote='', first_line_add='', indentation='    ', first_line_bold=True):
        indentation = (len(self.name) + 3) * ' ' # +3 because name is put in brackets and a space is added
        return(_fix_message(message=message, quote='', first_line_add='', indentation=indentation, first_line_bold=True))



class Input:

    def __init__(self, *args, **kwargs):
        self.name = ''
        if 'name' in kwargs:
            self.name = kwargs['name']

    def ask(self, question='', bold=True, color=''):
        indentation = (len(self.name) + 3) * ' ' # +3 because name is put in brackets and a space is added
        return(input(_fix_message(question, indentation=indentation) + '\n    '))
        '''
        if color != '' and bold == True:
            return(input(colorize(question, fg=color, opts=('bold',))))
        elif color != '' and bold == False:
            return(input(colorize(question, fg=color)))
        elif color == '' and bold == True:
            return(input(colorize(question, opts=('bold',))))
        elif color == '' and bold == False:
            log.error('You should just use input here.', kill=False)

        return(input(colorize(question)))
        '''


def get_or_default(message: str, default_variable: str, color='black', evaluate=str) -> str:
    inp = Input('')
    _ = inp.ask(f'{message} (default "{default_variable}"): ', color=color)
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
