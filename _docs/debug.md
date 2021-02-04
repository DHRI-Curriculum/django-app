# TODO


## Resetting all the data

A good one-line command to have handy is the following:

```sh
$ python manage.py build --forcedownload && python manage.py ingest --reset --force
```

Note that it will replace _everything_ in the database with the live data from GitHub.
