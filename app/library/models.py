from django.db import models


class Tutorial(models.Model):
    label = models.TextField(max_length=1000, blank=True, null=True)
    url = models.TextField(max_length=500, blank=True, null=True)
    comment = models.TextField(max_length=3000, blank=True, null=True)

    def __str__(self):
        return self.label


class Project(models.Model):
  title = models.TextField(max_length=500)
  url = models.TextField(max_length=500, null=True, blank=True)
  comment = models.TextField(max_length=3000, null=True, blank=True)
  zotero_item = models.TextField(max_length=500, null=True, blank=True)

  def __str__(self):
    return self.title


class Resource(models.Model):
  title = models.TextField(max_length=500)
  url = models.TextField(max_length=500)
  comment = models.TextField(max_length=3000, null=True, blank=True)
  zotero_item = models.TextField(max_length=500, null=True, blank=True)

  def __str__(self):
    return self.title


class Reading(models.Model):
  title = models.TextField(max_length=500)
  url = models.TextField(max_length=500)
  comment = models.TextField(max_length=3000, null=True, blank=True)
  zotero_item = models.TextField(max_length=500, null=True, blank=True)

  def __str__(self):
    return self.title
