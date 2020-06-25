from django.db import models

class Page(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, blank=True)
    text = models.TextField()
    is_homepage = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)