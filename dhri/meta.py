import argparse, re
from .constants import URL
from .log import dhri_error


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