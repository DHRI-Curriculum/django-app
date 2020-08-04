from django.db import models
from django.utils.text import slugify

class Term(models.Model):
    term = models.TextField()
    slug = models.CharField(max_length=200, blank=True)
    explication = models.TextField()
    readings = models.ManyToManyField('library.Reading')
    tutorials = models.ManyToManyField('library.Tutorial')

    def save(self, *args, **kwargs):
      name = self.name.replace('-',' ').replace('/',' ')
      self.slug = slugify(name)
      super(Workshop, self).save()