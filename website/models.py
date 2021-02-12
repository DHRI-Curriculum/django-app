from django.db import models



class Snippet(models.Model):
    identifier = models.CharField(max_length=50, unique=True)
    snippet = models.TextField()

    def __str__(self):
        return f'{self.identifier}'
