from django.db import models


class Frontmatter(models.Model):
  workshop = models.OneToOneField('workshop.Workshop', related_name="frontmatter", on_delete=models.CASCADE)
  abstract = models.TextField(max_length=1000, blank=True, null=True)
  # ethical_considerations = models.TextField(max_length=1000, blank=True, null=True)
  estimated_time = models.PositiveSmallIntegerField(blank=True, null=True, help_text="assign full minutes")
  projects = models.ManyToManyField('library.Project', related_name="frontmatters", blank=True)
  resources = models.ManyToManyField('library.Resource', related_name="frontmatters", blank=True)
  readings = models.ManyToManyField('library.Reading', related_name="frontmatters", blank=True)
  contributors = models.ManyToManyField('frontmatter.Contributor', related_name="frontmatters", blank=True)
  prerequisites = models.ManyToManyField('workshop.Workshop', related_name="prerequisites", blank=True)

  def __str__(self):
    return f'Frontmatter for {self.workshop.name}'


class LearningObjective(models.Model):
  frontmatter = models.ForeignKey(Frontmatter, on_delete=models.CASCADE, related_name="learning_objectives")
  label = models.TextField(max_length=500)

  def __str__(self):
    return f'{self.label}'


class EthicalConsideration(models.Model):
  frontmatter = models.ForeignKey(Frontmatter, on_delete=models.CASCADE, related_name="ethical_considerations")
  label = models.TextField(max_length=500)

  def __str__(self):
    return f'{self.label}'



class Contributor(models.Model):
  first_name = models.TextField(max_length=100)
  last_name = models.TextField(max_length=100)
  role = models.TextField(max_length=100, null=True, blank=True)
  url = models.TextField(max_length=200, null=True, blank=True)

  def _fullname(self):
    return self.first_name + ' ' + self.last_name

  _fullname.short_description = "Full name of contributor"
  _fullname.admin_order_field = 'last_name'

  full_name = property(_fullname)

  def __str__(self):
    return f'{self.full_name}'