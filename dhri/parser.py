from .log import dhri_error, dhri_log, dhri_warning
from .constants import MD_LIST_ELEMENTS, NUMBERS, URL, NORMALIZING_SECTIONS
from pathlib import Path
import json


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



def normalize_data(data, section):
  _ = {}
  for normalized_key, alts in NORMALIZING_SECTIONS[section].items():
      for alt in alts:
          done = False
          for key, val in data.items():
              if done:
                  continue
              if key.lower() == alt.lower():
                  _[normalized_key] = val
                  done = True
  return(_)

def parse_frontmatter(data):
  data = normalize_data(data, 'frontmatter')
  return(data)