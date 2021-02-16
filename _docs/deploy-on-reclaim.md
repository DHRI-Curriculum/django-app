# How to deploy on Reclaim Hosting

## Setting up a Django app on Reclaim

... [#TODO #362](https://github.com/DHRI-Curriculum/django-app/issues/362) = only for MySQL connection ([#313](https://github.com/DHRI-Curriculum/django-app/issues/313))

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

## Updating the Django app on Reclaim

### Step 1. Create a SSH connection

```console
$ ssh dhinstit@dhinstitutes.org
```

### Step 2. Activate Virtual Environment

```console
$ source virtualenv/curriculum.dhinstitutes.org/3.7/bin/activate
```

### Step 3. Navigate to Working Directory

```console
$ cd curriculum.dhinstitutes.org
```

### Step 4. Pull from GitHub and Ensure Branch Tracking

```console
$ git pull
```

If new/updated branches. For example (here `v1-dev`):

```console
$ git checkout --track origin/v1-dev
```

### Step 5. Collect Static Files

```console
$ python manage.py collectstatic
```

### Step 6. Load data

```console
$ python manage.py setup --wipe --all
```