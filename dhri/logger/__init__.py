from django.utils.termcolors import colorize
import textwrap

class Logger():
    def __init__(self, *args, **kwargs):
        pass

    def log(self, message="", kill=False, color='green'):
        message = self._process_message(message)
        message = colorize('--> ' + message, fg=color, opts=('',))
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

    def _process_message(self, message):
        message = message.split(": ")

        if len(message) >= 2:
            start_message = message[0]
            message = "".join(message[1:])
            message = "    " + "\n    ".join([x for x in textwrap.wrap(message, 66, break_long_words=False)])
            message = start_message + ":\n" + message

        elif len(message) == 1:
            message = "\n    ".join([x for x in textwrap.wrap(message[0], 66, break_long_words=False)])

        return(message)