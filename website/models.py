from django.db import models
from django.utils.translation import gettext_lazy as _
from backend.mixins import CurlyQuotesMixin


class Snippet(CurlyQuotesMixin, models.Model):
    curly_fields = ['snippet']

    identifier = models.CharField(max_length=50, unique=True)
    snippet = models.TextField()

    def __str__(self):
        return f'{self.identifier}'
