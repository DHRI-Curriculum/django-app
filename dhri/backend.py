from dhri.interaction import Logger, Input
from dhri.django.models import Contributor



""" def validate_existing(name, model=Workshop): # not currently in use
  # Validate whether database already contains workshop, and choose how to move on. Returns 0 (no workshop exists), 1 (one or more workshops exist so update latest), 2 (create duplicate workshop)
  existing = model.objects.filter(name=name).count()
  message = None
  if existing == 0:
    return(0)
  elif existing == 1:
    message = f'`{name}` of type {model.__name__} already exists - do you want to update (1) or create a new one (2)? '
  elif existing > 1:
    message = f'Multiple `{name}` of type {model.__name__} already exist - do you want to update the latest one (1) or create a new one (2)? '

  if message:
    validate = Input.ask(message, bold=True, color='')
    if validate not in ['1', '2']: log.error('Cancelled.')
    return(int(validate))
"""


""" # Not currently in use
def process_list(the_list: list, model):
  # Validates a list of list of names (the_list) against the database, asks the user whether to update with the new data or create a new database object with the same information. Return a list of the resulting ids, which can be inserted into a new database object.
  ids = []
  for name in the_list:
    existing = validate_existing(name, model=model)
    if existing == 0 or existing == 2:
      instance = model(
        name=name
      )
      instance.save()
      ids.append(instance.id)
    elif existing == 1:
      instance = model.objects.filter(name=name).last()
      # TODO: need to see examples before I update projects here
      instance.save()
      ids.append(instance.id)
  return(ids)
"""


def pre_process_contributors(the_list):
  """ Returns a list of tuples with the first name in the first location and all the last names in the second location. Won't work perfectly but it's as good as we can get it. """
  # TODO: #14 move pre_process_contributors to an earlier stage in the data processing (to dhri.parser?)
  return([(x.split(' ')[0], ' '.join(x.split(' ')[1:])) for x in the_list])


def process_contributors(the_list):
  ids = []
  for name in the_list:
    first_name, last_name = name
    # TODO: make the process with _everything_ more like this... it's a lot smarter, I think?
    if Contributor.objects.filter(first_name=first_name, last_name=last_name).count() == 0:
      # NOTE: The line above means that people who share first and last names will be confused by the script.
      p = Contributor(first_name=first_name, last_name=last_name)
      p.save()

    for obj in Contributor.objects.filter(first_name=first_name, last_name=last_name):
      if obj.id not in ids: ids.append(obj.id)

  return(ids)
