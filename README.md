# Digital Humanities Research Institute's curriculum website (Django)

This is the alpha 1 version of the DHRI's curriculum website (created as a django app), together with a script that can independently import data from a JSON file and populate the website.

Belongs to: Sprint 1  
Deadline: June 25

## Documentation

This repository contains two projects in one: **parse_json** and **app**. Some documentation is available below. It will be improved over the course of [the alpha versions](https://github.com/DHRI-Curriculum/django-app/releases) of this project.

### [parse_json](parse_json-README.md)

The first, **`parse_json`** is a pre-processing Python script that runs on the command line and helps set up the data for the second project, the **app** (see below). `parse_json` is designed to integrate with the curriculum transition and quickly populate the Django database.

### [app](app-README.md)

**app**, which is the Django application. The documentation of this app will follow the Django documentation.
