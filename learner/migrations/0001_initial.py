# Generated by Django 3.0.7 on 2021-02-14 14:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='default.jpg', upload_to='profile_pictures')),
                ('email_confirmed', models.BooleanField(default=False)),
                ('instructor_requested', models.BooleanField(default=False)),
                ('bio', models.TextField(blank=True, null=True)),
                ('pronouns', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=70)),
                ('url', models.URLField()),
                ('cat', models.CharField(choices=[('PE', 'Personal'), ('PR', 'Project')], default='PR', max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page', models.IntegerField(default=0)),
                ('modified', models.DateField(auto_now=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learner.Profile')),
            ],
        ),
    ]
