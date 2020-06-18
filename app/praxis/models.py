from django.db import models

class Praxis(models.Model):
  pass
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
  further_readings
  """

class Tutorials(models.Model):
  pass
  #further_readings
  #next_steps
  #discussion_questions
