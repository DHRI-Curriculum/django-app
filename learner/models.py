from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pictures')
    email_confirmed = models.BooleanField(default=False)
    favorites = models.ManyToManyField('workshop.Workshop', blank=True)
    instructor_requested = models.BooleanField(default=False)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}\'s Profile'