from pathlib import Path
import sys, re, argparse, json

from dhri.log import dhri_error, dhri_log, dhri_warning, Fore, Style
from dhri.parser import load_data, parse_frontmatter, test_integrity
from dhri.parser import NUMBERS, URL
from dhri.markdown_parser import get_raw_content, split_md_into_sections

if __name__ == "__main__":
  # Process arguments
  parser = argparse.ArgumentParser()
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument("-d", "--download", type=str, help="download from a directory")
  group.add_argument("-f", "--file", type=str, help="load data from a file containing JSON with processed data from a DHRI curriculum")
  group2 = group.add_argument_group()
  group2.add_argument('--dest', type=str, help="optional destination for download")
  args = parser.parse_args()
  if args.download:
    if not re.findall(URL, args.download):
      parser.error("-d must provide a valid URL to a DHRI repository.")

    dhri_log(f"URL accepted: {args.download}")

    data = get_raw_content(args.download, branch="v2.0")

    sections = {}
    sections['frontmatter'] = split_md_into_sections(data['content']['frontmatter'])
    sections['theory-to-practice'] = split_md_into_sections(data['content']['theory-to-practice'])
    sections['assessment'] = split_md_into_sections(data['content']['assessment'])

    if not "github" in args.download.lower():
      dhri_warning(f"Your URL seems to not originate with Github. Currently, our curriculum only works with Github as backend.")

    try:
      url_elems = args.download.split("/")
      user = url_elems[3]
      repo = url_elems[4]
    except:
      user, repo = args.download, args.download

    _user = input(f"Username (default '{user}')")
    if _user != "": user = _user

    _repo = input(f"Repository (default '{repo}')")
    if _repo != "": repo = _repo

    try:
      name = repo.replace("-", " ").title()
    except:
      name = repo

    _name = input(f"Workshop name (default '{name}')")
    if _name != "": name = _name

    sections['frontmatter']['Name'] = name
    sections['frontmatter']['Parent backend'] = "Github"
    sections['frontmatter']['Parent repo'] = f"{user}/{repo}"
    sections['frontmatter']['Parent branch'] = "v2.0"

    if args.dest: write_path = args.dest
    else: write_path = f"{repo}.json"

    Path(write_path).write_text(json.dumps(sections))
    dhri_log(f"File downloaded: {write_path}")

    _continue = input(Fore.YELLOW + "Do you want to continue with this file? (Y/n) " + Style.RESET_ALL)
    if _continue == "" or _continue.lower() == "y":
      json_file = write_path
    else:
      exit()

  elif args.file:
    json_file = args.file
  else:
    args.error("Cannot interpret the arguments passed to the script. Try running it with argument -h to see more information.")

  # Now we load up the backend
  from dhri.backend import validate_existing, create_new_workshop, update_workshop, Workshop, Frontmatter, Project, Resource, Literature, Contributor

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