from django.db import models
from django.urls import reverse
from backend.mixins import CurlyQuotesMixin
from backend.dhri.text import dhri_slugify


class Term(CurlyQuotesMixin, models.Model):
    curly_fields = ['explication']

    term = models.TextField()
    slug = models.CharField(max_length=200, blank=True, unique=True)
    explication = models.TextField()
    readings = models.ManyToManyField('library.Reading')
    tutorials = models.ManyToManyField('library.Tutorial')

    def save(self, *args, **kwargs):
        self.slug = dhri_slugify(self.term)
        super(Term, self).save()

    def __str__(self):
        return f'{self.term}'

    class Meta:
        ordering = ['term']

    def get_absolute_url(self):
        return reverse('glossary:letter', kwargs={'letter': self.term[0].upper(), 'slug': self.slug})
