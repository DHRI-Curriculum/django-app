# Generated by Django 3.0.7 on 2021-02-09 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson', '0002_lessonimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessonimage',
            name='url',
            field=models.URLField(unique=True),
        ),
    ]
