# Generated by Django 3.0.7 on 2020-08-06 22:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('glossary', '0002_term_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='term',
            options={'ordering': ['term']},
        ),
    ]