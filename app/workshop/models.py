from django.db import models
from django.utils.text import slugify

class Workshop(models.Model):
  name = models.CharField(max_length=200)
  slug = models.CharField(max_length=200, blank=True)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  parent_backend = models.CharField(max_length=100, blank=True, null=True)
  parent_repo = models.CharField(max_length=100, blank=True, null=True)
  parent_branch = models.CharField(max_length=100, blank=True, null=True)

  def save(self, *args, **kwargs):
      self.slug = slugify(self.name.replace('-',' '))
      super(Workshop, self).save()

  def __str__(self):
    return(self.name)
