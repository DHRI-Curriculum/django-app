# Generated by Django 3.0.7 on 2020-08-25 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('install', '0007_screenshot_gh_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screenshot',
            name='gh_name',
            field=models.CharField(max_length=500),
        ),
    ]