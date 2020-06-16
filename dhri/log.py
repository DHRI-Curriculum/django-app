from django.utils.termcolors import colorize


def _test_kill(message, kill):
  if kill:
    exit(message)
  else:
    print(message)


def dhri_log(message):
  message = colorize("--> " + message, fg="green", opts=('',))
  print(message)


def dhri_error(message, kill=True):
  message = colorize("Error: " + message, fg="red", opts=('bold',))
  _test_kill(message, kill)


def dhri_warning(message, kill=False):
  message = colorize("Warning: " + message, fg="yellow", opts=('bold',))
  _test_kill(message, kill)


def dhri_input(message, bold=True, color=""):
  if color != "" and bold == True:
    return(input(colorize(message, fg=color, opts=('bold',))))
  elif color != "" and bold == False:
    return(input(colorize(message, fg=color)))
  elif color == "" and bold == True:
    return(input(colorize(message, opts=('bold',))))
  elif color == "" and bold == False:
    print("You can just use input here.")
    return(input(colorize(message)))