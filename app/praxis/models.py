from django.db import models
from frontmatter.models import Reading


class Tutorial(models.Model):
    label = models.TextField(max_length=1000, blank=True, null=True)
    url = models.TextField(max_length=500, blank=True, null=True)
    comment = models.TextField(max_length=3000, blank=True, null=True)


class Praxis(models.Model):
    discussion_questions = models.TextField(max_length=3000, blank=True, null=True)
    next_steps = models.TextField(max_length=3000, blank=True, null=True)
    further_readings = models.ManyToManyField(Reading)
    

    """
    workshop = models.OneToOneField('workshop.Workshop', related_name="frontmatter", on_delete=models.CASCADE)
    abstract = models.TextField(max_length=1000, blank=True, null=True)
    learning_objectives = models.TextField(max_length=1000, blank=True, null=True)
    ethical_considerations = models.TextField(max_length=1000, blank=True, null=True)
    estimated_time = models.PositiveSmallIntegerField(blank=True, null=True, help_text="assign full minutes")
    projects = models.ManyToManyField('frontmatter.Project', related_name="frontmatters", blank=True)
    resources = models.ManyToManyField('frontmatter.Resource', related_name="frontmatters", blank=True)
    readings = models.ManyToManyField('frontmatter.Reading', related_name="frontmatters", blank=True)
    contributors = models.ManyToManyField('frontmatter.Contributor', related_name="frontmatters", blank=True)
    prerequisites = models.ManyToManyField('workshop.Workshop', related_name="prerequisites", blank=True)
    """