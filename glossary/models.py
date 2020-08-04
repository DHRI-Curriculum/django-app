from django.db import models

class Term(models.Model):
    term = models.TextField()
    explication = models.TextField()
    readings = models.ManyToManyField('library.Reading')
    tutorials = models.ManyToManyField('library.Tutorial')