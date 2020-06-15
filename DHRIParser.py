from DHRIlog import dhri_error, dhri_log, dhri_warning
from pathlib import Path
import json

# Regex setup
MD_LIST_ELEMENTS = r"\- (.*)(\n|$)"
NUMBERS = r"(\d+([\.,][\d+])?)"



def load_data(json_file):
  dhri_log(f"loading {json_file}")

  if not Path(json_file).exists():
    dhri_error(f"Could not find JSON file on path: {json_file}")

  data = json.loads(Path(json_file).read_text())
  return(data)



# Data integrity tests

def test_integrity(data):
  # Test for required name
  if not 'frontmatter' in data: dhri_error(f"`frontmatter` section missing in submitted JSON data.")
  if not 'Name' in data['frontmatter']: dhri_error(f"`Required `Name` in frontmatter missing in submitted JSON data.")

  # Test for sections in data
  missing_sections = list({'frontmatter', 'theory-to-practice', 'assessment'} - set(data.keys()))
  for section in missing_sections:
    dhri_error(f"`{section}` section missing in submitted JSON data.")

  # in the following, we call `dhri_warning` when the model defines the field as `null=True`

  test_sections = [
    {'section': 'abstract', 'human': 'abstract', 'null': True, 'type': str},
    {'section': 'acknowledgements', 'human': 'acknowledgements', 'null': True, 'type': str},
    {'section': 'estimated time', 'human': 'estimated time', 'null': True, 'type': int},
    {'section': 'ethical considerations', 'human': 'ethical considerations', 'null': True, 'type': str},
    {'section': 'learning objective', 'human': 'learning objectives', 'null': True, 'type': list},
    {'section': 'reading', 'human': 'readings', 'null': True, 'type': list},
    {'section': 'project', 'human': 'projects', 'null': True, 'type': list},
    {'section': 'resource', 'human': 'resources', 'null': True, 'type': list},
    {'section': 'parent backend', 'human': 'parent backend', 'null': True, 'type': tuple},
    {'section': 'parent repo', 'human': 'parent repository', 'null': True, 'type': tuple},
    {'section': 'parent branch', 'human': 'parent branch', 'null': True, 'type': tuple},
  ]
  lower_sections = [x.lower() for x in data['frontmatter'].keys()]

  for test in test_sections:
    passed_existing = False
    for _ in lower_sections:
      if test['section'] in _:
        passed_existing = True
        # TODO: test for type here as well

    if not passed_existing:
      if test['null'] == True: dhri_warning(f"No {test['human']} section (optional) in frontmatter in submitted JSON.")
      elif test['null'] == False: dhri_error(f"No {test['human']} section (required) in frontmatter in submitted JSON.")

    # TODO: check whether type test passed.


def parse_frontmatter(data):
  abstract, name, contributors, estimated_time, ethical_considerations, learning_objectives, readings, projects, resources = None, None, None, None, None, None, None, None, None
  for key in data:
    val = data[key]
    check = key.lower()

    if "abstract" in check: abstract = val
    elif "name" in check: name = val
    elif "acknowledgements" in check: contributors = val
    elif "estimated time" in check: estimated_time = val
    elif "ethical consideration" in check: ethical_considerations = val
    elif "learning objective" in check: learning_objectives = val
    elif "reading" in check: readings = val
    elif "project" in check: projects = val
    elif "resource" in check: resources = val
    elif "parent backend" in check: parent_backend = val
    elif "parent repo" in check: parent_repo = val
    elif "parent branch" in check: parent_branch = val

  return({
    'name': name,
    'abstract': abstract,
    'contributors': contributors,
    'estimated_time': estimated_time,
    'learning_objectives': learning_objectives,
    'ethical_considerations': ethical_considerations,
    'readings': readings,
    'projects': projects,
    'resources': resources,
    'parent_backend': parent_backend,
    'parent_repo': parent_repo,
    'parent_branch': parent_branch,
  })
