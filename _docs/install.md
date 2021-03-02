# Installing `django-app` on a Local Server

## Step 1. Clone the repository

First, clone this directory to your local computer by navigating to the parent directory where you want to place the `django-app` folder, and then running the following command:

```sh
$ git clone https://github.com/DHRI-Curriculum/django-app
Cloning into 'django-app'...
...
Resolving deltas: 100% (1843/1843), done.
```

![Animated GIF showing the result from running the `git clone` command above, illustrating the text-representation above.](images/01-clone.gif)

After it is finished, navigate into the repository, using:

```sh
$ cd django-app
```

![Animated GIF showing the `cd django-app` command.](images/02-cd-django-app.gif)

## Step 2. Create virtual enviroment

Next, create a virtual environment for Django to run in:

```sh
$ python -m venv env
```

Then activate the environment:

```sh
$ source env/bin/activate
```

![Animated GIF showing visually how to start a Python virtual environment, reflecting the text-instructions above.](images/03-virtual-environment.gif)

## Step 3: Install requirements

The script contains a `requirements.txt` file in the root of the repository, which makes it easy for you to run a command to run all the required dependencies:

```sh
$ pip install -r requirements.txt
Collecting django==3.0.7 (from -r requirements.txt (line 1))
  ...
```

That should show you the progress of the installation of all the python dependencies for the project.

![Animated GIF showing the result of the `pip install` command from the example above.](images/04-pip-install.gif)

# Step 4: Add your secrets

Set up all your secrets as environment variables:

```sh
$ SECRET_KEY="<create a django secret key here>"
```

```sh
$ EMAIL_HOST_USER="<insert your email user here>"
$ EMAIL_HOST_PASSWORD="<insert your email password here>"
$ GITHUB_TOKEN="<insert your GitHub token here>"
```

## Optional step: Backup solution

If you want to create a backup solution for the secret keys, put the values (with no surrounding quotation marks) of them into a text file with the name for the variable into the `./app/.secrets/` directory. Thus, the directory should look as follows:

```
django-app
|
|--- app
   |
   |---- .secrets
      |
      |--- SECRET_KEY
      |--- EMAIL_HOST_USER
      |--- EMAIL_HOST_PASSWORD
      |--- GITHUB_TOKEN
      |
```

---

### Continue install track

[<< Back to documentation](README.md) | [Next step >>](populate.md)