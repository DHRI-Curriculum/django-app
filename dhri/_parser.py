from pathlib import Path
import re

from dhri.interaction import Logger
from dhri.constants import _test
from dhri.utils.regex import NUMBERS
from dhri.settings import NORMALIZING_SECTIONS, REQUIRED_SECTIONS

# Data integrity tests

log = Logger()

def test_for_keys(key_set=None, dictionary=None, dictionary_name='', lower=True, exact=True):
  """ Checks whether a dictionary has all keys.
  Lowers the keys if lower is set to True (default).
  Exact (default True) whether exact matches of key_set values are in the dictionary's keys. If not checked, it uses Python's "in"
  """
  _test(key_set, set)
  _test(dictionary, dict)
  
  check_keys = [x for x in dictionary.keys()]
  if lower: check_keys = [x.lower() for x in check_keys]

  if exact == True:
    missing_sections = list(key_set - set(check_keys))
  
    for section in missing_sections:
      log.error(f'`{section}` section missing in dictionary ({dictionary_name}).')
  
  elif exact == False:
    for section in list(key_set - set(check_keys)):
      ok = False
      for _ in check_keys:
        if section in _: ok = True
      if ok == False:
        log.error(f'`{section}` section missing in dictionary ({dictionary_name}).')


def test_integrity(data):
  # Test for required name
  test_for_keys({'meta', 'frontmatter', 'theory-to-practice', 'assessment'}, data, 'data')
  test_for_keys({'name'}, data['meta'], 'meta in data')
  test_for_keys(REQUIRED_SECTIONS['frontmatter'], data['frontmatter'], 'frontmatter in data', exact=True)
  
  return(True)


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


def normalize_number(assumed_integer):
  g = re.search(NUMBERS, assumed_integer)
  if g:
    if '.' in g.groups()[0]:
      assumed_integer = g.groups()[0].split('.')[0]
    else:
      assumed_integer = g.groups()[0]
  else:
    assumed_integer = 0
  return(assumed_integer)


def parse(data, data_type: str) -> dict:
  log.log(f'Parsing {data_type} for workshop...')
  
  data = normalize_data(data, data_type)
  
  if data_type == 'frontmatter':
    data['estimated_time'] = normalize_number(data['estimated_time'])
  
  return(data)
