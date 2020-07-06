from django.db import models
from library.models import Reading, Project, Resource, Tutorial
from workshop.models import Workshop

class Praxis(models.Model):
    discussion_questions = models.TextField(max_length=3000, blank=True, null=True)
    next_steps = models.TextField(max_length=3000, blank=True, null=True)
    further_readings = models.ManyToManyField(Reading)
    more_projects = models.ManyToManyField(Project)
    more_resources = models.ManyToManyField(Resource)
    tutorials = models.ManyToManyField(Tutorial)
    workshop = models.OneToOneField(Workshop, on_delete=models.CASCADE)

    def __str__(self):
        return f'Praxis collection for workshop {self.workshop.name}'
