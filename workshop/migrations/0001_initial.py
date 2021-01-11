# Generated by Django 3.1.4 on 2021-01-11 22:20

import backend.mixins
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('library', '0001_initial'),
        ('learner', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Collaboration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('Au', 'Author'), ('Re', 'Reviewer'), ('Ed', 'Editor')], default='Au', max_length=2)),
                ('current', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('current',),
            },
        ),
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.TextField(max_length=100)),
                ('last_name', models.TextField(max_length=100)),
                ('url', models.TextField(blank=True, max_length=200, null=True)),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='learner.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Frontmatter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abstract', models.TextField()),
                ('estimated_time', models.PositiveSmallIntegerField(blank=True, help_text='assign full minutes', null=True)),
                ('contributors', models.ManyToManyField(blank=True, related_name='frontmatters', through='workshop.Collaboration', to='workshop.Contributor')),
            ],
            bases=(backend.mixins.CurlyQuotesMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Workshop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.CharField(blank=True, max_length=200, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('parent_backend', models.CharField(blank=True, max_length=100, null=True)),
                ('parent_repo', models.CharField(blank=True, max_length=100, null=True)),
                ('parent_branch', models.CharField(blank=True, max_length=100, null=True)),
                ('views', models.PositiveSmallIntegerField(default=0)),
                ('image', models.ImageField(default='workshop_headers/default.jpg', upload_to='workshop_headers/')),
            ],
        ),
        migrations.CreateModel(
            name='Praxis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intro', models.TextField(blank=True, max_length=3000, null=True)),
                ('further_projects', models.ManyToManyField(related_name='praxis', to='library.Project')),
                ('further_readings', models.ManyToManyField(related_name='praxis', to='library.Reading')),
                ('more_resources', models.ManyToManyField(related_name='praxis', to='library.Resource')),
                ('tutorials', models.ManyToManyField(related_name='praxis', to='library.Tutorial')),
                ('workshop', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='workshop.workshop')),
            ],
            options={
                'verbose_name_plural': 'praxes',
            },
            bases=(backend.mixins.CurlyQuotesMixin, models.Model),
        ),
        migrations.CreateModel(
            name='NextStep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField(max_length=500)),
                ('order', models.PositiveSmallIntegerField()),
                ('praxis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='next_steps', to='workshop.praxis')),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(backend.mixins.CurlyQuotesMixin, models.Model),
        ),
        migrations.CreateModel(
            name='LearningObjective',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField(max_length=500)),
                ('frontmatter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_objectives', to='workshop.frontmatter')),
            ],
            bases=(backend.mixins.CurlyQuotesMixin, models.Model),
        ),
        migrations.AddField(
            model_name='frontmatter',
            name='prerequisites',
            field=models.ManyToManyField(blank=True, related_name='prerequisites', to='workshop.Workshop'),
        ),
        migrations.AddField(
            model_name='frontmatter',
            name='projects',
            field=models.ManyToManyField(blank=True, related_name='frontmatters', to='library.Project'),
        ),
        migrations.AddField(
            model_name='frontmatter',
            name='readings',
            field=models.ManyToManyField(blank=True, related_name='frontmatters', to='library.Reading'),
        ),
        migrations.AddField(
            model_name='frontmatter',
            name='resources',
            field=models.ManyToManyField(blank=True, related_name='frontmatters', to='library.Resource'),
        ),
        migrations.AddField(
            model_name='frontmatter',
            name='workshop',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='frontmatter', to='workshop.workshop'),
        ),
        migrations.CreateModel(
            name='EthicalConsideration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField(max_length=500)),
                ('frontmatter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ethical_considerations', to='workshop.frontmatter')),
            ],
            bases=(backend.mixins.CurlyQuotesMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DiscussionQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField(max_length=500)),
                ('order', models.PositiveSmallIntegerField()),
                ('praxis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discussion_questions', to='workshop.praxis')),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(backend.mixins.CurlyQuotesMixin, models.Model),
        ),
        migrations.AddField(
            model_name='collaboration',
            name='contributor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collaborations', to='workshop.contributor'),
        ),
        migrations.AddField(
            model_name='collaboration',
            name='frontmatter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workshop.frontmatter'),
        ),
        migrations.CreateModel(
            name='Blurb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('workshop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workshop.workshop')),
            ],
            bases=(backend.mixins.CurlyQuotesMixin, models.Model),
        ),
    ]
