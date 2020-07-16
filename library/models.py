from django.db import models


class Tutorial(models.Model):
  label = models.TextField(max_length=1000, blank=True, null=True)
  url = models.TextField(max_length=500, blank=True, null=True)
  annotation = models.TextField(max_length=3000, blank=True, null=True)
  zotero_item = models.TextField(max_length=500, null=True, blank=True)

  def __str__(self):
    return f'{self.label}'


class Project(models.Model):
  title = models.TextField(max_length=500, null=True)
  url = models.TextField(max_length=500, null=True, blank=True)
  annotation = models.TextField(max_length=3000, null=True, blank=True)
  zotero_item = models.TextField(max_length=500, null=True, blank=True)

  def __str__(self):
    return f'{self.title}'


class Resource(models.Model):
  title = models.TextField(max_length=500)
  url = models.TextField(max_length=500)
  annotation = models.TextField(max_length=3000, null=True, blank=True)
  zotero_item = models.TextField(max_length=500, null=True, blank=True)

  def __str__(self):
    return f'{self.title}'


class Reading(models.Model):
  title = models.TextField(max_length=500, null=True)
  url = models.TextField(max_length=500, null=True)
  annotation = models.TextField(max_length=3000, null=True, blank=True)
  zotero_item = models.TextField(max_length=500, null=True, blank=True)

  def __str__(self):
    return f'{self.title}'