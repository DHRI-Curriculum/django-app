from django.db import models
from django.utils.text import slugify
from install.models import Software
from backend.mixins import CurlyQuotesMixin
#from backend.dhri.text import dhri_slugify


def dhri_slugify(string: str) -> str: # TODO: Move to backend.dhri.text
    import re
    from django.utils.text import slugify
    # first replace any non-OK characters [/] with space
    string = re.sub(r'[\/\-\–\—\_]', '', string)

    # then replace space with -
    string = re.sub(r'\s', '-', string)

    # then replace too many spaces with one space
    string = re.sub(r'\s+', ' ', string)

    # then replace any characters that are not in ALLOWED charset with nothing
    string = re.sub(r'[^a-zA-Z\-\s]', '', string)

    # finally, use Django's slugify
    string = slugify(string)

    return string
    

class Insight(CurlyQuotesMixin, models.Model):
    curly_fields = ['text']

    title = models.CharField(max_length=80, unique=True)
    slug = models.CharField(max_length=200, blank=True)
    software = models.ManyToManyField(Software)
    text = models.TextField(blank=True, null=True)
    # TODO: Add image field

    def save(self, *args, **kwargs):
        self.title = dhri_slugify(self.title)
        super(Insight, self).save()

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = ['title']


class Section(CurlyQuotesMixin, models.Model):
    curly_fields = ['text']

    insight = models.ForeignKey(
        Insight, on_delete=models.CASCADE, related_name='sections')
    order = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=80)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = ['order']


class OperatingSystemSpecificSection(CurlyQuotesMixin, models.Model):
    curly_fields = ['text']

    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='os_specific_sections')
    operating_system = models.CharField(max_length=80)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'OS Specific Instructions for section {self.section.title}'
