from django.db import models

class Frontmatter(models.Model):
  workshop = models.OneToOneField('workshop.Workshop', related_name="frontmatter", on_delete=models.CASCADE)
  abstract = models.TextField(max_length=1000, blank=True, null=True)
  learning_objectives = models.TextField(max_length=1000, blank=True, null=True)
  ethical_considerations = models.TextField(max_length=1000, blank=True, null=True)
  estimated_time = models.PositiveSmallIntegerField(blank=True, null=True, help_text="assign full minutes")
  projects = models.ManyToManyField('frontmatter.Project', related_name="frontmatters", blank=True)
  resources = models.ManyToManyField('frontmatter.Resource', related_name="frontmatters", blank=True)
  readings = models.ManyToManyField('frontmatter.Literature', related_name="frontmatters", blank=True)
  contributors = models.ManyToManyField('frontmatter.Contributor', related_name="frontmatters", blank=True)
  prerequisites = models.ManyToManyField('workshop.Workshop', related_name="prerequisites", blank=True)


  def __str__(self):
    return("Frontmatter for " + self.workshop.name)

class Project(models.Model):
  name = models.TextField(max_length=200)
  url = models.TextField(max_length=200)

  def __str__(self):
    return(self.name)


class Resource(models.Model):
  name = models.TextField(max_length=200)
  url = models.TextField(max_length=200)

  def __str__(self):
    return(self.name)


class Literature(models.Model):
  name = models.TextField(max_length=200)
  url = models.TextField(max_length=200)

  def __str__(self):
    return(self.name)


class Contributor(models.Model):
  first_name = models.TextField(max_length=50)
  last_name = models.TextField(max_length=50)

  def _fullname(self):
    return self.first_name + ' ' + self.last_name
  _fullname.short_description = "Full name of contributor"
  _fullname.admin_order_field = 'last_name'

  full_name = property(_fullname)

  def __str__(self):
    return(self.full_name)