# Generated by Django 3.0.7 on 2021-02-13 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(max_length=500, null=True)),
                ('url', models.TextField(max_length=500, null=True)),
                ('annotation', models.TextField(blank=True, max_length=3000, null=True)),
                ('zotero_id', models.TextField(blank=True, max_length=500, null=True)),
                ('category', models.CharField(choices=[('uncategorized', 'Uncategorized'), ('reading', 'Reading'), ('project', 'Project'), ('tutorial', 'Tutorial')], default='uncategorized', max_length=13)),
            ],
            options={
                'unique_together': {('title', 'url', 'category', 'annotation')},
            },
        ),
    ]
