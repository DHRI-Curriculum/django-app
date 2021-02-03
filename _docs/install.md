# Installing

## Step 1. Clone the repository

```sh
$ git clone https://github.com/DHRI-Curriculum/django-app
Cloning into 'django-app'...
...
Resolving deltas: 100% (1843/1843), done.
```

Then navigate into the repository (`cd django-app`).

## Step 2. Create virtual enviroment

Next, create a virtual environment for Django to run in:

```sh
$ python -m venv env
```

Then activate the environment:

```sh
$ source env/bin/activate
```

## Step 3: Install requirements

The script contains a `requirements.txt` file in the root of the repository, which makes it easy for you to run a command to run all the required dependencies:

```sh
$ pip install -r requirements.txt
Collecting django==3.0.7 (from -r requirements.txt (line 1))
  ...
```

That should show you the progress of the installation of all the python dependencies for the project.

# Step 4: Add your secrets

In a file inside the `app/secrets.py` directory, put the following information:

```py
SECRET_KEY = '<create a django secret key here>'
EMAIL_HOST_USER = '<insert your email user here>'
EMAIL_HOST_PASSWORD = '<insert your email password here>'
GITHUB_TOKEN = '<insert your GitHub token here>'
ZOTERO_KEY = '<this can be left empty for now>'
```

If you have Visual Studio Code installed, you can just type the following command and copy and paste the structure from above into the window that opens, change your information, and then close and save the file:

```sh
code app/secrets.py
```

Of course, you can make the same edits with whichever plain text editor you prefer to use.

---

### Continue install track

[<< Back to repo](https://github.com/DHRI-Curriculum/django-app/tree/alpha-3) | [Next step >>](populate.md)