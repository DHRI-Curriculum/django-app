from django.db import models
from frontmatter.models import Reading


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
    
    def __str__(self):
        return 'praxis object -- needs FK to a workshop!'