from django.db import models
from django.utils.text import slugify
from library.models import Reading, Project, Resource, Tutorial


class Workshop(models.Model):
  name = models.CharField(max_length=200)
  slug = models.CharField(max_length=200, blank=True)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  parent_backend = models.CharField(max_length=100, blank=True, null=True)
  parent_repo = models.CharField(max_length=100, blank=True, null=True)
  parent_branch = models.CharField(max_length=100, blank=True, null=True)
  views = models.PositiveSmallIntegerField(default=0)

  def save(self, *args, **kwargs):
      name = self.name.replace('-',' ').replace('/',' ')
      self.slug = slugify(name)
      super(Workshop, self).save()

  def __str__(self):
      return f'{self.name}'

  @property
  def terms(self):
      "Returns all the terms associated with all lessons belonging to workshop."
      _ = list()
      for lesson in self.lessons.all():
        _.extend(lesson.terms.all())
      return(_)

  @property
  def has_terms(self):
    for lesson in self.lessons.all():
        if lesson.terms.count(): return True
    return False



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


class Frontmatter(models.Model):
  workshop = models.OneToOneField(Workshop, related_name="frontmatter", on_delete=models.CASCADE)
  abstract = models.TextField(max_length=1000, blank=True, null=True)
  # ethical_considerations = models.TextField(max_length=1000, blank=True, null=True)
  estimated_time = models.PositiveSmallIntegerField(blank=True, null=True, help_text="assign full minutes")
  projects = models.ManyToManyField('library.Project', related_name="frontmatters", blank=True)
  resources = models.ManyToManyField('library.Resource', related_name="frontmatters", blank=True)
  readings = models.ManyToManyField('library.Reading', related_name="frontmatters", blank=True)
  contributors = models.ManyToManyField(Contributor, related_name="frontmatters", blank=True)
  prerequisites = models.ManyToManyField(Workshop, related_name="prerequisites", blank=True)

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


class Praxis(models.Model):
    discussion_questions = models.TextField(max_length=3000, blank=True, null=True)
    next_steps = models.TextField(max_length=3000, blank=True, null=True)
    further_readings = models.ManyToManyField(Reading, related_name='praxis')
    more_projects = models.ManyToManyField(Project, related_name='praxis')
    more_resources = models.ManyToManyField(Resource, related_name='praxis')
    tutorials = models.ManyToManyField(Tutorial, related_name='praxis')
    workshop = models.OneToOneField(Workshop, on_delete=models.CASCADE)

    def __str__(self):
        return f'Praxis collection for workshop {self.workshop.name}'
