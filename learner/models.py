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

    def personal_links(self):
        return self.links.filter(cat='PE')

    def project_links(self):
        return self.links.filter(cat='PR')

class ProfileLink(models.Model):
    PERSONAL = 'PE'
    PROJECT = 'PR'
    CAT_CHOICES = [
        (PERSONAL, 'Personal'),
        (PROJECT, 'Projects'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links')
    label = models.CharField(max_length=70)
    url = models.URLField()
    cat = models.CharField(max_length=2, choices=CAT_CHOICES, default=PROJECT)

    def __str__(self):
        return f'{self.url}'