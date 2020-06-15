from pathlib import Path
import sys, re

from dhri.log import dhri_error, dhri_log, dhri_warning
from dhri.parser import load_data, parse_frontmatter, test_integrity, NUMBERS
from dhri.backend import validate_existing, create_new_workshop, update_workshop, Workshop, Frontmatter, Project, Resource, Literature, Contributor


if __name__ == "__main__":
  # Process arguments
  # TODO: add a `--download` argument, which should be able to download any given repository using the now implemented `markdown_parser` functions in the dhri library.
  if not len(sys.argv) > 1: dhri_error("Path to JSON file must be provided as first argument to script.")
  json_file = sys.argv[1]

  data = load_data(json_file) # Load data from json_file
  test_integrity(data) # Test data integrity


  existing = validate_existing(data['frontmatter']['Name'])


  # Start parsing

  ## frontmatter
  frontmatter = parse_frontmatter(data['frontmatter'])

  ## TODO: add other parsers here (below `parse_frontmatter`)


  # TODO: *temporarily here* here, I fix the numbers for the estimated time, which should not be done here but rather in the parser, so this should be removed/moved to DHRIParser.py
  ########################################################################
  g = re.search(NUMBERS, frontmatter['estimated_time'])
  if g:
    if "." in g.groups()[0]:
      frontmatter['estimated_time'] = g.groups()[0].split(".")[0]
    else:
      frontmatter['estimated_time'] = g.groups()[0]
  else:
    frontmatter['estimated_time'] = 0
  ########################################################################



  if existing == 0 or existing == 2:
    w = create_new_workshop(frontmatter)
  elif existing == 1:
    w = update_workshop(frontmatter)
