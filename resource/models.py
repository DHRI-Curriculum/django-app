from django.db import models
from backend.mixins import CurlyQuotesMixin


class Resource(CurlyQuotesMixin, models.Model):
    curly_fields = ['annotation']

    UNCATEGORIZED = 'uncategorized'
    READING = 'reading'
    PROJECT = 'project'
    TUTORIAL = 'tutorial'
    CATEGORY_CHOICES = [
        (UNCATEGORIZED, 'Uncategorized'),
        (READING, 'Reading'),
        (PROJECT, 'Project'),
        (TUTORIAL, 'Tutorial')
    ]
    CATEGORY_CHOICES_PLURAL = [
        (UNCATEGORIZED, 'Uncategorized'),
        (READING, 'Readings'),
        (PROJECT, 'Projects'),
        (TUTORIAL, 'Tutorials')
    ]

    title = models.TextField(max_length=500, null=True)
    url = models.TextField(max_length=500, null=True)
    annotation = models.TextField(max_length=3000, null=True, blank=True)
    zotero_id = models.TextField(max_length=500, null=True, blank=True)
    category = models.CharField(
        max_length=13, choices=CATEGORY_CHOICES, default=UNCATEGORIZED)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        unique_together = ['title', 'url', 'category', 'annotation']
