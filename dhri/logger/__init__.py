from django.utils.termcolors import colorize


class Logger():
    def __init__(self, *args, **kwargs):
        pass
        
    def log(self, message="", kill=False):
        message = colorize('--> ' + message, fg='green', opts=('',))
        print(message)

    def error(self, message="", raise_error=False, kill=True):
        if raise_error != None:
            raise(raise_error(message))
        message = colorize('Error: ' + message, fg='red', opts=('bold',))
        self._test_kill(message, kill)

    def warning(self, message="", kill=False):
        message = colorize('Warning: ' + message, fg='yellow', opts=('bold',))
        self._test_kill(message, kill)

    def _test_kill(self, message="", kill=False):
        if kill == True:
            exit(message)
        else:
            print(message)