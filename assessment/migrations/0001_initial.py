# Generated by Django 3.0.7 on 2021-05-21 19:06

import adminsortable.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField(max_length=500)),
                ('order', models.PositiveSmallIntegerField(db_index=True, default=0, editable=False)),
                ('question_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assessment.QuestionType')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField(max_length=500)),
                ('order', models.PositiveSmallIntegerField(db_index=True, default=0, editable=False)),
                ('is_correct_answer', models.BooleanField(default=False)),
                ('question', adminsortable.fields.SortableForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer', to='assessment.Question')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
