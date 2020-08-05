from django.db import models
from django.utils.text import slugify

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