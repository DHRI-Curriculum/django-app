import argparse, re
from .constants import URL


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
