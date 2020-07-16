#!/bin/bash
python3.8 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt 

python populate.py

rm -rf ./app/db.sqlite3

python ./app/manage.py makemigrations
python ./app/manage.py migrate

python ./app/manage.py loaddata ./app/fixtures.json

export DJANGO_SUPERUSER_EMAIL="noemail@none.com"
export DJANGO_SUPERUSER_USERNAME="admin"
export DJANGO_SUPERUSER_PASSWORD="admin"
python ./app/manage.py createsuperuser --noinput

python -mwebbrowser http://127.0.0.1:8000/admin && python ./app/manage.py runserver
