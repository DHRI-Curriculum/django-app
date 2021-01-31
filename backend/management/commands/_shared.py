from django.utils.text import slugify
import pathlib, yaml, re


def test_for_required_files(REQUIRED_PATHS=[], log=None):
    for test in REQUIRED_PATHS:
        path, error_msg = test
        if not pathlib.Path(path).exists():
            return log.error(error_msg)

    return True


def get_yaml(file):
    with open(file, 'r+') as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)


def get_name(path):
    return path.split('/')[-1].replace('.py', '')


def dhri_slugify(string: str) -> str:  # TODO: Move to backend.dhri.text
    # first replace any non-OK characters [/] with space
    string = re.sub(r'[\/\-\–\—\_]', ' ', string)

    # then replace too many spaces with one space
    string = re.sub(r'\s+', ' ', string)

    # then replace space with -
    string = re.sub(r'\s', '-', string)

    # then replace any characters that are not in ALLOWED charset with nothing
    string = re.sub(r'[^a-zA-Z\-\s]', '', string)

    # finally, use Django's slugify
    string = slugify(string)

    return string
