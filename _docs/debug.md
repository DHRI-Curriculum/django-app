# TODO


## Resetting all the data

A good one-line command to have handy is the following:

```sh
$ python manage.py build --forcedownload && python manage.py ingest --reset --force
```

Note that it will replace _everything_ in the database with the live data from GitHub.

This is another super-reset command:

```sh
$ find . -path "*/migrations/*.py" -not -name "__init__.py" -delete && find . -path "*/migrations/*.pyc"  -delete && rm db.sqlite3 && python manage.py makemigrations && python manage.py migrate && python manage.py build && python manage.py ingest
```