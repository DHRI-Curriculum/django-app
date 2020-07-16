# Populate Database

The Django app comes with built-in support to download all the data from the DHRI Curriculum, in a number of different ways. The most straight-forward way is what follows.

## Step 1. Set up database structure

First, set up the database by running two commands from Django's built-in management script:

```sh
$ python manage.py makemigrations
```

```sh
$ python manage.py migrate
```

## Step 2. Populate with live data

Next, run the custom DHRI command from inside Django's own management script:

```sh
$ python manage.py downloaddata --wipe --all
```

- The `--wipe` parameter resets the database (so it is not necessary if you have just cloned this repository but it's good to keep there to run some housekeeping tasks in other cases).

- The `--all` parameter will download data from _all_ the standard repositories. If you want to see the full list, just run `python manage.py showsettings --repo`. Should you want to make edits, see ["Changing settings"](#changing-settings) below.

---

## Optional: Populate selectively

### Groups

If you want to populate the database with the **automatic groups**, you can run:

```sh
$ python manage.py loadgroups
```

_Note that `loadgroups` will replace any groups found with the same name, without informing you._

### Users

If you want to populate the database with the **automatic users**, you can run:

```sh
$ python manage.py loadusers
```

_Note that `loadusers` will replace any users found with the same username, without informing you._

### Pages

If you want to populate the database with the **automatic pages**, you can run:

```sh
$ python manage.py loadpages
```

_Note that `loadpages` will **not** replace pages found with the same title but inform you that they have not been saved._

---

### Continue install track

[<< Previous step](install.md) | [Next step >>](run.md)