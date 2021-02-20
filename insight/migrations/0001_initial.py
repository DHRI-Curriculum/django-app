# Generated by Django 3.0.7 on 2021-02-20 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('install', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Insight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=80, unique=True)),
                ('slug', models.CharField(blank=True, max_length=200, unique=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(default='insight_headers/default.png', upload_to='insight_headers/')),
                ('image_alt', models.TextField(blank=True, null=True)),
                ('software', models.ManyToManyField(to='install.Software')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField()),
                ('title', models.CharField(max_length=80)),
                ('text', models.TextField(blank=True, null=True)),
                ('insight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='insight.Insight')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='OperatingSystemSpecificSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operating_system', models.CharField(max_length=80)),
                ('text', models.TextField(blank=True, null=True)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='os_specific_sections', to='insight.Section')),
            ],
        ),
    ]
