from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Term(models.Model):
    term = models.TextField()
    slug = models.CharField(max_length=200, blank=True)
    explication = models.TextField()
    readings = models.ManyToManyField('library.Reading')
    tutorials = models.ManyToManyField('library.Tutorial')

    def save(self, *args, **kwargs):
        term = self.term.replace('-',' ').replace('/',' ')
        self.slug = slugify(term)
        super(Term, self).save()

    def __str__(self):
        return f'{self.term}'

    class Meta:
        ordering = ['term']

    def get_absolute_url(self):
        return reverse('glossary:letter', kwargs={'letter': self.term[0].upper(), 'slug': self.slug })