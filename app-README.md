# django-app

Contents:

1. [Installing](#1-installing)
2. [Populate Database](#2-populate-database)
3. [Run Server](#3-run-server)
4. [Advanced: Enable Access on Local Network](#4-enable-access-on-local-network-advanced)  
   [Footnotes](#footnotes)

---

## Two Central Files

Before we begin, it is good for you to keep track of two files:

```
— django-app  
|  
+— app  
|  |  
|  +— manage.py  <—— django
|  
+— populate.py   <—— DHRI-specific
```

`manage.py` is the central tool for Django, and you will need it, most importantly, to run the server, but also to set up databases, etc. In this repository it is located inside `django-app` > `app`.

`populate.py` is the central tool for populating Django's database with DHRI-specific content. It is located in the `django-app` root directory.

#### This manual focuses primarily on Django (`manage.py`). [Populate-README](populate-README.md) focuses on the options for the `populate.py` script.

---

## 1. Installing

### Step 1. Install Dependencies

Run the following command on your command line:

```
pip3 install django
```

### Step 2: Clone Repository

First, navigate to the directory where you want to clone the repository — ie. `cd ~/Desktop` if you want to place it on your desktop.

Then, run on your command line:

```
git clone https://github.com/DHRI-Curriculum/django-app
```

### Step 3: Setup Database Structure

First, create the migrations for the Django database by running on your command line:

```
python django-app/app/manage.py makemigrations
```

Next, you need to migrate the database by running:

```
python django-app/app/manage.py migrate
```

### (Optional Step: Create Superuser)

Finally, you might want to setup a superuser for the database. A "superuser" in Django is an admin that has all the power over the database structure and its contents.

If you do, just run the following command:

```
python django-app/app/manage.py createsuperuser
```

The tool will ask you for some information and you must provide it with a username and a password. _If your password is weak, the tool will ask whether you want to override the protection against weak passwords. If you're only using this installation for development purposes, you can accept a weak password. In production, you do not want to do so._

---

## 2. Populate Database

In order to populate the database with some live data, we will use the `populate.py` tool that is available in the `django-app` repository.† (Documentation on the tool is available [here](populate-README.md).)

Run the following command on your command line:

```
python django-app/populate.py -d https://www.github.com/kallewesterling/dhri-test-repo
```

_(Note that you may need to adjust the path to `populate.py` above, depending on your current working directory.)_

---

## 3. Run Server

Now, you are all done. You can run the server by finding the `manage.py` tool that we have referred to multiple times above, and running this command:

```
python manage.py runserver
```

_It will automatically create a development server for you, and you should be able to now navigate to http://localhost:8000 (or its alias http://127.0.0.1:8000)_ in a browser on your computer._

---

## 4. Enable Access on Local Network (Advanced)

If you want to make your development server accessible through your local network, you can do so by following these steps:

### Step 1: Adjust Settings

- Edit the file `django-app/app/app/settings.py`

- Find the line that (most likely) reads:
   ```python
   ALLOWED_HOSTS = []
   ```
   ...and change it to:
   ```python
   ALLOWED_HOSTS = ['*']
   ```

### Step 2: Run Server

Instead of the command in the Run Server section above, run the following command:

```
python manage.py runserver 0.0.0.0:80
```

### Done!

Now you should be able

---

## Footnotes

(†) Because we are still in development mode, for now, we will use some model data from a `dhri-test-repo` repository. In production, these repositories will change to the workshop repositories.