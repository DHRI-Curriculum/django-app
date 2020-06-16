from pathlib import Path
import re, json

from dhri.log import dhri_error, dhri_log, dhri_warning, dhri_input
from dhri.parser import parse_frontmatter, test_integrity
from dhri.constants import *
from dhri.markdown_parser import get_raw_content, split_md_into_sections
from dhri.meta import get_argparser, verify_url, load_data, save_data, get_or_default


# Set up empty variables
sections, sections['meta'] = {}, {}


if __name__ == "__main__":
  # Process arguments
  parser = get_argparser()
  args = parser.parse_args()

  # First check for reset
  if args.reset:
    _continue = dhri_input("Are you sure you want to reset the entire DHRI curriculum in the current Django database? (y/N) ", bold=True, color="red")
    if _continue.lower() == "y":
      from dhri.backend import Workshop, Frontmatter, Project, Resource, Literature, Contributor
      for _ in [Workshop, Frontmatter, Project, Resource, Literature, Contributor]:
        _.objects.all().delete()
        dhri_log(f"All {_.__name__} deleted.")
      exit()
    else:
      exit()

  if args.download:
    url = verify_url(args.download)
    
    branch = get_or_default("Branch", BRANCH_AUTO)

    data = get_raw_content(url, branch=branch)

    user = get_or_default("Username", data['meta']['user'])
    repo = get_or_default("Repository", data['meta']['repo_name'])
    name = get_or_default("Workshop name", repo.replace("-", " ").title())
    
    sections['meta']['name'] = name
    sections['meta']['Parent repo'] = f"{user}/{repo}"
    sections['meta']['Parent backend'] = BACKEND_AUTO
    sections['meta']['Parent branch'] = data['meta']['branch']

    sections['frontmatter'] = split_md_into_sections(data['content']['frontmatter'])
    sections['theory-to-practice'] = split_md_into_sections(data['content']['theory-to-practice'])
    sections['assessment'] = split_md_into_sections(data['content']['assessment'])


    path = f"{repo}.json"
    if args.dest: path = args.dest

    save_data(path, sections)

    _continue = dhri_input("Do you want to continue with this file? (Y/n) ", bold=True, color="yellow")
    if _continue == "" or _continue.lower() == "y":
      pass # we continue
    else:
      exit()

  elif args.file:
    path = args.file

  else:
    args.error("Cannot interpret the arguments passed to the script. Try running it with argument -h to see more information.")

  # Now we load up the backend (we do it here because we don't want to load the whole django framework before, because it takes a second)
  from dhri.backend import validate_existing, workshop_magic, create_new_workshop, update_workshop, Workshop, Frontmatter, Project, Resource, Literature, Contributor

  data = load_data(path)
  
  # Parse data
  data['frontmatter'] = parse_frontmatter(data['frontmatter']) # TODO: add other parsers after `parse_frontmatter`
  
  # Test integrity for the data
  test_integrity(data)

  w = workshop_magic(sections['meta'], data['frontmatter'])

"""
  if existing == 0 or existing == 2:
    w = create_new_workshop(frontmatter)
  elif existing == 1:
    w = update_workshop(frontmatter)
"""