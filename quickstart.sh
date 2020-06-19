#!/bin/bash
python3.7 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt 
python ./app/manage.py makemigrations
python ./app/manage.py migrate
python ./app/manage.py loaddata ./app/fixtures.json
python ./app/manage.py createsuperuser
python ./app/manage.py runserver
