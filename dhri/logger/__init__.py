from django.utils.termcolors import colorize

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
        pass

    def log(self, message="", kill=False, color='green'):
        message = _fix_message(message)
        message = colorize(message, fg=color, opts=('',))
        self.write(message)

    def error(self, message="", raise_error=None, kill=True, color='red'):
        if raise_error != None:
            raise(raise_error(message))
        message = colorize('Error: ' + message, fg=color, opts=('bold',))
        self.write(message, kill)

    def warning(self, message="", kill=False, color='yellow'):
        message = colorize('Warning: ' + message, fg=color, opts=('bold',))
        self.write(message, kill)

    def write(self, message:str, kill=False):
        if kill == True:
            exit(message)
        else:
            print(message)

