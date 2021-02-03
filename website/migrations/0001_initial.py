# Generated by Django 3.1.4 on 2021-02-03 01:42

import backend.mixins
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Snippet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=50, unique=True)),
                ('snippet', models.TextField()),
            ],
            bases=(backend.mixins.CurlyQuotesMixin, models.Model),
        ),
    ]
