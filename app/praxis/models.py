from django.db import models
from frontmatter.models import Reading
from workshop.models import Workshop


class Tutorial(models.Model):
    label = models.TextField(max_length=1000, blank=True, null=True)
    url = models.TextField(max_length=500, blank=True, null=True)
    comment = models.TextField(max_length=3000, blank=True, null=True)
    
    def __str__(self):
        return self.label


class Praxis(models.Model):
    discussion_questions = models.TextField(max_length=3000, blank=True, null=True)
    next_steps = models.TextField(max_length=3000, blank=True, null=True)
    further_readings = models.ManyToManyField(Reading)
    tutorials = models.ManyToManyField(Tutorial)
    workshop = models.OneToOneField(Workshop, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'Praxis collection for workshop {self.workshop.name}'
