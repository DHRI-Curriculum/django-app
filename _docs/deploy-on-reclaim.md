# How to deploy on Reclaim Hosting

## Setting up a Django app on Reclaim

...

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

If new/updated branches. For example (here `alpha-5`):

```console
$ git checkout --track origin/alpha-5
```

### Step 5. Collect Static Files

```console
$ python manage.py collectstatic
```

### Step 6. Load data

```console
$ python manage.py setup --wipe --all
```