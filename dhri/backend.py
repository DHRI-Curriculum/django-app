import sys, os, django
from .log import dhri_error, dhri_log, dhri_warning, dhri_input

dhri_log(f'setting up database interaction...')

sys.path.append('./app')
os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings'
django.setup()

from .models import *

def validate_existing(name, model=Workshop):
  """ Validate whether database already contains workshop, and choose how to move on. Returns 0 (no workshop exists), 1 (one or more workshops exist so update latest), 2 (create duplicate workshop) """
  existing = model.objects.filter(name=name).count()
  message = None
  if existing == 0:
    return(0)
  elif existing == 1:
    message = f'`{name}` of type {model.__name__} already exists - do you want to update (1) or create a new one (2)? '
  elif existing > 1:
    message = f'Multiple `{name}` of type {model.__name__} already exist - do you want to update the latest one (1) or create a new one (2)? '

  if message:
    validate = dhri_input(message, bold=True, color='')
    if validate not in ['1', '2']: dhri_error('Cancelled.')
    return(int(validate))


def process_list(the_list, model):
  """ Validates a list of list of names (the_list) against the database, asks the user whether to update with the new data or create a new database object with the same information. Return a list of the resulting ids, which can be inserted into a new database object. """
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



def workshop_magic(data):
  name = data['meta']['name']
  
  dhri_log(f'Processing workshop {name}')
  
  w = Workshop.objects.filter(name=name)
  if len(w):
    new = False
  elif len(w) == 0:
    new = True
  
  if new == False:
    _continue = input(f'Update existing Workshop {name} with frontmatter from json file? (y/N) ')
    if _continue.lower() == 'y':
      print('update')
    else:
      _continue = input(f'Add a new Workshop {name} with frontmatter from json file? (y/N) ')
      if _continue.lower() == 'y':
        print('insert new')
        new = True
      else:
        print('no update')
        return(False) # TODO: OK?
  
  if new == False:
    w = Workshop.objects.latest('created')

  if new == True:
    w = Workshop(name=name)
    w.save()
  
  data['frontmatter']['workshop'] = w

  lists = {}
  for list_element, model in {'projects': Project, 'resources': Resource, 'readings': Literature}.items():
    list_ = data['frontmatter'].pop(list_element)
    ids = []
    for name in list_:
      e = model(name=name) # TODO: This does not yet test whether the list_element already exists, and provides the user with a test whether they want to update/create new
      e.save()
      if e.id not in ids: ids.append(e.id)
    lists[list_element] = ids
  
  contributors = pre_process_contributors(data['frontmatter'].pop('contributors'))
  ids = []
  for contributor in contributors:
    first_name, last_name = contributor
    c = Contributor(first_name=first_name, last_name=last_name) # TODO: This does not yet test whether the list_element already exists, and provides the user with a test whether they want to update/create new
    c.save()
    if c.id not in ids: ids.append(c.id)
  lists['contributors'] = ids
  
  f = Frontmatter.objects.create(**data['frontmatter'])

  for list_element, ids in lists.items():
    if list_element == 'projects': f.projects.set(ids)
    elif list_element == 'resources': f.resources.set(ids)
    elif list_element == 'readings': f.readings.set(ids)
    elif list_element == 'contributors': f.contributors.set(ids)
    else:
      dhri_error('Encountered unknown list element.', raise_error=RuntimeError)

  f.save()
    
  



def update_workshop(data):
  w = Workshop.objects.latest('created')
  
  dhri_log(f'Updating workshop {w}')

  w.parent_backend = data['meta']['parent_backend']
  w.parent_repo = data['meta']['parent_repo']
  w.parent_branch = data['meta']['parent_branch']

  dhri_log(f'Adding frontmatter information for workshop {w}')

  w.frontmatter.ethical_considerations = data['frontmatter']['ethical_considerations']

  ids = process_list(data['frontmatter']['projects'], Project)
  w.frontmatter.projects.set(ids)
  dhri_log(f'Projects {ids} have been updated in frontmatter.')

  ids = process_list(data['frontmatter']['resources'], Resource)
  w.frontmatter.resources.set(ids)
  dhri_log(f'Resources {ids} have been updated in frontmatter.')

  ids = process_list(data['frontmatter']['readings'], Literature)
  w.frontmatter.readings.set(ids)
  dhri_log(f'Readings {ids} have been updated in frontmatter.')

  contributors = pre_process_contributors(data['frontmatter']['contributors'])
  ids = process_contributors(contributors)
  w.frontmatter.contributors.set(ids)
  dhri_log(f'Contributors {ids} have been updated in frontmatter.')

  w.save()

  dhri_log(f'{w} (id {w.id}) has been updated.')

  return(w)


def create_new_workshop(data):
  name = data['meta']['name']
  dhri_log(f'Creating {name}')
  w = Workshop(
        name = name,
        parent_backend = data['meta']['parent_backend'],
        parent_repo = data['meta']['parent_repo'],
        parent_branch = data['meta']['parent_branch']
      )
  w.save()

  dhri_log(f'{w} (id {w.id}) has been created.')

  f = Frontmatter(
        workshop = w,
        abstract = data['frontmatter']['abstract'],
        learning_objectives = data['frontmatter']['learning_objectives'],
        ethical_considerations = data['frontmatter']['ethical_considerations'],
        estimated_time = data['frontmatter']['estimated_time']
      )
  f.save()

  dhri_log(f'{f} (id {f.id}) has been created.')

  ids = process_list(data['frontmatter']['projects'], Project)
  f.projects.set(ids)
  dhri_log(f'Projects {ids} have been added to frontmatter.')

  ids = process_list(data['frontmatter']['resources'], Resource)
  f.resources.set(ids)
  dhri_log(f'Resources {ids} have been added to frontmatter.')

  ids = process_list(data['frontmatter']['readings'], Literature)
  f.readings.set(ids)
  dhri_log(f'Readings {ids} have been added to frontmatter.')

  contributors = pre_process_contributors(data['frontmatter']['contributors'])
  ids = process_contributors(contributors)
  f.contributors.set(ids)
  dhri_log(f'Contributors {ids} have been added to frontmatter.')

  f.save()

  dhri_log(f'{f} (id {f.id}) has been updated with all the necessary information.')

  # Final warning about pre-requisites
  dhri_warning(f'Pre-requisites are not programmatically added, but must be added through the Django admin interface.')

  return(w)
