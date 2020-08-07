from django.db import models
from django.contrib.auth.models import User

class Issue(models.Model):
    lesson = models.ForeignKey('lesson.Lesson', on_delete=models.CASCADE)
    workshop = models.ForeignKey('workshop.Workshop', on_delete=models.CASCADE)
    website = models.BooleanField(default=False)
    open = models.BooleanField(default=True)
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues', null=True, blank=True)

    def __str__(self):
        return f'Issue opened by {self.user.username}'