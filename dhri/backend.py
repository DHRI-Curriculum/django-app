import sys, os, django, json
from .log import dhri_error, dhri_log, dhri_warning, dhri_input

dhri_log(f"setting up database interaction...")

sys.path.append('./app')
os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings'
django.setup()

from workshop.models import Workshop
from frontmatter.models import Frontmatter, Project, Resource, Literature, Contributor


def validate_existing(name, model=Workshop):
  """ Validate whether database already contains workshop, and choose how to move on. Returns 0 (no workshop exists), 1 (one or more workshops exist so update latest), 2 (create duplicate workshop) """
  existing = model.objects.filter(name=name).count()
  message = None
  if existing == 0:
    return(0)
  elif existing > 1:
    message = f"Multiple `{name}` of type {model.__name__} already exist - do you want to update the latest one (1) or create a new one (2)? "
  elif existing == 1:
    message = f"`{name}` of type {model.__name__} already exists - do you want to update (1) or create a new one (2)? "

  if message:
    validate = dhri_input(message, bold=True, color="")
    if validate not in ["1", "2"]: dhri_error("Cancelled.")
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
  return([(x.split(" ")[0], " ".join(x.split(" ")[1:])) for x in the_list])


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


def update_workshop(frontmatter):
  dhri_log(f"Updating workshop {frontmatter['name']}")
  update_id = Workshop.objects.latest('created').id
  w = Workshop.objects.get(pk=update_id)

  w.parent_backend = frontmatter['parent_backend']
  w.parent_repo = frontmatter['parent_repo']
  w.parent_branch = frontmatter['parent_branch']

  dhri_log(f"Adding frontmatter information for workshop {frontmatter['name']}")

  w.frontmatter.ethical_considerations = frontmatter['ethical_considerations']

  ids = process_list(frontmatter['projects'], Project)
  w.frontmatter.projects.set(ids)
  dhri_log(f"Projects {ids} have been updated in frontmatter.")

  ids = process_list(frontmatter['resources'], Resource)
  w.frontmatter.resources.set(ids)
  dhri_log(f"Resources {ids} have been updated in frontmatter.")

  ids = process_list(frontmatter['readings'], Literature)
  w.frontmatter.readings.set(ids)
  dhri_log(f"Readings {ids} have been updated in frontmatter.")

  contributors = pre_process_contributors(frontmatter['contributors'])
  ids = process_contributors(contributors)
  w.frontmatter.contributors.set(ids)
  dhri_log(f"Contributors {ids} have been updated in frontmatter.")

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

  f = Frontmatter(
        workshop = w,
        abstract = frontmatter['abstract'],
        learning_objectives = frontmatter['learning_objectives'],
        ethical_considerations = frontmatter['ethical_considerations'],
        estimated_time = frontmatter['estimated_time']
      )
  f.save()

  dhri_log(f"{f} (id {f.id}) has been created.")

  ids = process_list(frontmatter['projects'], Project)
  f.projects.set(ids)
  dhri_log(f"Projects {ids} have been added to frontmatter.")

  ids = process_list(frontmatter['resources'], Resource)
  f.resources.set(ids)
  dhri_log(f"Resources {ids} have been added to frontmatter.")

  ids = process_list(frontmatter['readings'], Literature)
  f.readings.set(ids)
  dhri_log(f"Readings {ids} have been added to frontmatter.")

  contributors = pre_process_contributors(frontmatter['contributors'])
  ids = process_contributors(contributors)
  f.contributors.set(ids)
  dhri_log(f"Contributors {ids} have been added to frontmatter.")

  f.save()

  dhri_log(f"{f} (id {f.id}) has been updated with all the necessary information.")

  # Final warning about pre-requisites
  dhri_warning(f"Pre-requisites are not programmatically added, but must be added through the Django admin interface.")

  return(w)
