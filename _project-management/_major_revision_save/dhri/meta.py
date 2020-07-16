import argparse, json, os, re
from pathlib import Path

from dhri.interaction import Logger, Input
from dhri.utils.regex import URL
from dhri.utils.exceptions import UnresolvedNameOrBranch

log = Logger(name="meta")
inp = Input(name="meta")

def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument('-d', '--download', type=str, help='download from a directory')
    g.add_argument('-f', '--file', type=str, help='load data from a file containing JSON with processed data from a DHRI curriculum')
    g.add_argument('-r', '--reset', action='store_true', help='reset the DHRI curriculum data in the database')
    
    g2 = g.add_argument_group()
    g2.add_argument('--dest', type = str, help = 'optional destination for download')
    
    return(parser)


def confirm_url(url: str) -> bool:
    """Confirm that the string tested is a URL"""
    if re.findall(URL, url):
        return(True)
    return(False)


def verify_url(url: str) -> str:
    if not confirm_url(url):
        log.error(f'You must provide a valid URL to a DHRI repository. {url} was not accepted.', raise_error=UnresolvedNameOrBranch)
    if not 'github' in url.lower():
        log.error(f'Your URL seems to not originate with Github. Currently, our curriculum only works with Github as backend.', raise_error=NotImplementedError)
    log.log(f'URL accepted: {url}')
    return(url)


def load_data(path: str) -> dict:
  log.log(f'Loading {path}')

  if not Path(path).exists():
    log.error(f'Could not find JSON file on path: {path}')

  data = json.loads(Path(path).read_text())
  return(data)


def test_path(path: str) -> bool:
    """Tests the pathname"""
    if not path.endswith('.json'):
        log.warning(f'The data file ({path}) is not saved as a .json file. It will work but it might be confusing.')
    return(True)


def save_data(path: str, data: dict) -> bool:
    test_path(path)
    Path(path).write_text(json.dumps(data))
    log.log(f'File saved to {path}')
    return(True)


def delete_data(path, auto=False):
    if auto == False:
      _continue = inp.ask(f'Are you sure you want to delete the data file ({path})? (y/N) ', bold=True, color='red')
      if _continue.lower() != 'y':
        exit()
    else:
      log.warning('Deleting file (DELETE_FILE set to True)...')
    
    Path(path).unlink()
