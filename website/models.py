from django.db import models
from django.utils.translation import gettext_lazy as _
from backend.mixins import CurlyQuotesMixin


class Page(models.Model):
    class Template(models.TextChoices):
        STANDARD = 'website/page.html', _('Standard')
        WORKSHOP_LIST = 'workshop/workshop-list.html', _('Workshop list')
        LIBRARY_LIST = 'library/index.html', _('Library items')

    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, blank=True)
    text = models.TextField()
    template = models.CharField(
        max_length=100, choices=Template.choices, default=Template.STANDARD)
    is_homepage = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'


class Snippet(CurlyQuotesMixin, models.Model):
    curly_fields = ['snippet']

    identifier = models.CharField(max_length=50, unique=True)
    snippet = models.TextField()

    def __str__(self):
        return f'{self.identifier}'
