from colorama import Fore, Style
from colorama import init as colorama_init

colorama_init()

def _format_message(clr, message):
  return clr + message + Style.RESET_ALL

def _test_kill(message, kill):
  if kill:
    exit(message)
  else:
    print(message)

def dhri_log(message):
  message = _format_message(Fore.GREEN, message)
  print("-->", message)

def dhri_error(message, kill=True):
  message = _format_message(Fore.RED, message)
  _test_kill(message, kill)

def dhri_warning(message, kill=False):
  message = _format_message(Fore.YELLOW, "Warning: " + message)
  _test_kill(message, kill)