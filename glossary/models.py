from django.db import models
from django.urls import reverse
from backend.dhri_utils import dhri_slugify


class Term(models.Model):
    term = models.TextField()
    slug = models.CharField(max_length=200, blank=True, unique=True)
    explication = models.TextField()
    readings = models.ManyToManyField('resource.Resource', related_name='term_readings')
    tutorials = models.ManyToManyField('resource.Resource', related_name='term_tutorials')
    cheat_sheets = models.ManyToManyField('resource.Resource', related_name='term_cheat_sheets')

    def save(self, *args, **kwargs):
        if self.term:
            self.slug = dhri_slugify(self.term)
        else:
            pass # no term provided...
        super(Term, self).save()

    def __str__(self):
        return f'{self.term}'

    class Meta:
        ordering = ['slug']

    def get_absolute_url(self):
        return reverse('glossary:letter', kwargs={'letter': self.term[0].upper(), 'slug': self.slug})
