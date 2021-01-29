import pathlib, yaml

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