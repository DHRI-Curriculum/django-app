# App-specific settings

Required files to add for the app to run:

In the `root` directory (likely `curriculum.dhinstitutes.org`), `sql.cnf` with the following contents:

```
[client]
database = <dhinstit_curriculum>
user = <user with access>
password = <password for username>
default-character-set = utf8
host = dhinstitutes.org
port = 3306
sql_mode = STRICT_TRANS_TABLES
```

In the `app` directory, `secrets.py` with the following contents:

```py
SECRET_KEY = '<insert secret django key here>'
EMAIL_HOST_USER = '<username for the email server (set up in app/settings.py)>'
EMAIL_HOST_PASSWORD = '<password for the username above>'
GITHUB_TOKEN = '<github token>'
```
