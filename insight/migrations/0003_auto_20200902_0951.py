# Generated by Django 3.0.7 on 2020-09-02 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insight', '0002_auto_20200902_0951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insight',
            name='text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='operatingsystemspecificsection',
            name='text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='text',
            field=models.TextField(blank=True, null=True),
        ),
    ]