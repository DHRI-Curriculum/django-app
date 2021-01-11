from django.db import models
from django.contrib.auth.models import User

class Issue(models.Model):
    from workshop.models import Workshop
    from lesson.models import Lesson

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, related_name='issues')
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues', null=True, blank=True)
    website = models.BooleanField(default=False)
    open = models.BooleanField(default=True)
    comment = models.TextField()

    def __str__(self):
        return f'Issue opened by {self.user.username}'