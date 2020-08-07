from django.db import models
from django.contrib.auth.models import User

class Issue(models.Model):
    lesson = models.ForeignKey('lesson.Lesson', on_delete=models.CASCADE, null=True, blank=True)
    workshop = models.ForeignKey('workshop.Workshop', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues', null=True, blank=True)
    website = models.BooleanField(default=False)
    open = models.BooleanField(default=True)
    comment = models.TextField()

    def __str__(self):
        return f'Issue opened by {self.user.username}'