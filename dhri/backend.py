import sys, os, django, json
from .log import dhri_error, dhri_log, dhri_warning, _format_message, Fore


dhri_log(f"setting up database interaction...")

sys.path.append('./app')
os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings'
django.setup()

from workshop.models import Workshop
from frontmatter.models import Frontmatter, Project, Resource, Literature, Contributor


def validate_existing(name, model=Workshop):
  existing = model.objects.filter(name=name).count()
  message = None
  if existing == 0:
    return(0)
  elif existing > 1:
    message = f"Multiple `{name}` of type {model.__name__} already exist - do you want to update the latest one (1) or create a new one (2)? "
  elif existing == 1:
    message = f"`{name}` of type {model.__name__} already exists - do you want to update (1) or create a new one (2)? "

  if message:
    validate = input(_format_message(Fore.YELLOW, message))
    if validate not in ["1", "2"]: dhri_error("Cancelled.")
    return(int(validate))



def process_list(the_list, model):
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
      # TODO: need to see examples befpre I update projects here
      instance.save()
      ids.append(instance.id)
  return(ids)


def update_workshop(frontmatter):
  dhri_log(f"Updating {frontmatter['name']}")
  update_id = Workshop.objects.latest('created').id
  w = Workshop.objects.get(pk=update_id)
  print(w.frontmatter)
  print(w.frontmatter.projects)
  
  w.parent_backend = frontmatter['parent_backend']
  w.parent_repo = frontmatter['parent_repo']
  w.parent_branch = frontmatter['parent_branch']
  # TODO: map all the values from frontmatter on here `w.XXXXX = frontmatter['XXXXXXX']

  ids = process_list(frontmatter['projects'], Project)
  w.frontmatter.projects.set(ids)

  ids = process_list(frontmatter['resources'], Resource)
  w.frontmatter.resources.set(ids)

  ids = process_list(frontmatter['readings'], Literature)
  w.frontmatter.readings.set(ids)

  w.save()

  dhri_log(f"{w} (id {w.id}) has been updated.")

  return(w)


def create_new_workshop(frontmatter):
  dhri_log(f"Creating {frontmatter['name']}")
  w = Workshop(
        name = frontmatter['name'],
        parent_backend = frontmatter['parent_backend'],
        parent_repo = frontmatter['parent_repo'],
        parent_branch = frontmatter['parent_branch']
      )
  w.save()

  dhri_log(f"{w} (id {w.id}) has been created.")

  # TODO: branch out into all the related information here and create them
  '''
          projects
          resources
          readings
          contributors
          prerequisites
          ethical_considerations
  '''

  f = Frontmatter(
        workshop = w,
        abstract = frontmatter['abstract'],
        learning_objectives = frontmatter['learning_objectives'],
        estimated_time = frontmatter['estimated_time'],
      )
  f.save()

  return(w)
