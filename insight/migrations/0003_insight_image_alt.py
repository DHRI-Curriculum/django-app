# Generated by Django 3.0.7 on 2021-02-05 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insight', '0002_insight_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='insight',
            name='image_alt',
            field=models.TextField(blank=True, null=True),
        ),
    ]