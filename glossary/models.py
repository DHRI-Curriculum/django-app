from django.db import models
from django.urls import reverse
from backend.mixins import CurlyQuotesMixin
# from backend.dhri.text import dhri_slugify


def dhri_slugify(string: str) -> str: # TODO: #363 Move to backend.dhri.text
    import re
    from django.utils.text import slugify
    # first replace any non-OK characters [/] with space
    string = re.sub(r'[\/\-\–\—\_]', ' ', string)

    # then replace too many spaces with one space
    string = re.sub(r'\s+', ' ', string)

    # then replace space with -
    string = re.sub(r'\s', '-', string)


    # then replace any characters that are not in ALLOWED charset with nothing
    string = re.sub(r'[^a-zA-Z\-\s]', '', string)

    # finally, use Django's slugify
    string = slugify(string)

    return string


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
