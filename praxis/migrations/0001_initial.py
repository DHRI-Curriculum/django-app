# Generated by Django 3.0.7 on 2020-07-16 18:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('library', '0001_initial'),
        ('workshop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Praxis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discussion_questions', models.TextField(blank=True, max_length=3000, null=True)),
                ('next_steps', models.TextField(blank=True, max_length=3000, null=True)),
                ('further_readings', models.ManyToManyField(related_name='praxis', to='library.Reading')),
                ('more_projects', models.ManyToManyField(related_name='praxis', to='library.Project')),
                ('more_resources', models.ManyToManyField(related_name='praxis', to='library.Resource')),
                ('tutorials', models.ManyToManyField(related_name='praxis', to='library.Tutorial')),
                ('workshop', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='workshop.Workshop')),
            ],
        ),
    ]