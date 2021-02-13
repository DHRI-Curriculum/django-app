from django.db import models
from django.utils.text import slugify
from install.models import Software
from backend.dhri_utils import dhri_slugify


class Insight(models.Model):
    title = models.CharField(max_length=80, unique=True)
    slug = models.CharField(max_length=200, blank=True, unique=True)
    software = models.ManyToManyField(Software)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to='insight_headers/', default='insight_headers/default.png')
    image_alt = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = dhri_slugify(self.title)
        super(Insight, self).save()

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = ['title']


class Section(models.Model):
    insight = models.ForeignKey(
        Insight, on_delete=models.CASCADE, related_name='sections')
    order = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=80)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = ['order']


class OperatingSystemSpecificSection(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='os_specific_sections')
    operating_system = models.CharField(max_length=80)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'OS Specific Instructions for section {self.section.title}'
