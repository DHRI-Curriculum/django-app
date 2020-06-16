import argparse, re, json
from pathlib import Path
from .constants import URL, AUTO_RESET
from .log import dhri_log, dhri_warning, dhri_error


def get_argparser():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--download", type=str, help="download from a directory")
    group.add_argument("-f", "--file", type=str, help="load data from a file containing JSON with processed data from a DHRI curriculum")
    group.add_argument("-r", "--reset", action='store_true', help="reset the DHRI curriculum data in the database")
    group2 = group.add_argument_group()
    group2.add_argument('--dest', type=str, help="optional destination for download")
    return(parser)


def confirm_url(string):
    """ Confirm that the string tested is a URL """
    if re.findall(URL, string):
        return(True)
    return(False)


def verify_url(string):
    if not confirm_url(string):
        dhri_error("-d must provide a valid URL to a DHRI repository.")
    if not "github" in string.lower():
        dhri_error(f"Your URL seems to not originate with Github. Currently, our curriculum only works with Github as backend.") # Set to kill out of the program
    dhri_log(f"URL accepted: {string}")
    return(string)


def load_data(path):
  dhri_log(f"Loading {path}")

  if not Path(path).exists():
    dhri_error(f"Could not find JSON file on path: {path}")

  data = json.loads(Path(path).read_text())
  return(data)


def test_path(path):
    """ Tests the pathname """
    if not path.endswith(".json"):
        dhri_warning("The data file is not saved as a .json file. It will work but it might be confusing.")
    return(True)


def save_data(path, data):
    test_path(path)
    Path(path).write_text(json.dumps(data))
    dhri_log(f"File saved to {path}")
    return(True)


def get_or_default(message, default_variable):
    _ = input(f"{message} (default '{default_variable}'): ")
    if _ != "":
        return(_)
    else:
        return(default_variable)


def reset_all(kill=True):
    if AUTO_RESET == False:
      _continue = dhri_input("Are you sure you want to reset the entire DHRI curriculum in the current Django database? (y/N) ", bold=True, color="red")
      if _continue.lower() != "y":
        exit()
    else:
      dhri_warning("Resetting database (AUTO_RESET set to True)...")

    from dhri.backend import Workshop, Frontmatter, Project, Resource, Literature, Contributor
    for _ in [Workshop, Frontmatter, Project, Resource, Literature, Contributor]:
        _.objects.all().delete()
    dhri_log(f"All {_.__name__} deleted.", kill=not AUTO_RESET)