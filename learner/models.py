from workshop.models import Workshop
from django.db import models
from django.contrib.auth.models import User



class Profile(models.Model):    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg',
                              upload_to='profile_pictures')
    email_confirmed = models.BooleanField(default=False)
    favorites = models.ManyToManyField(Workshop, blank=True)
    instructor_requested = models.BooleanField(default=False)
    bio = models.TextField(null=True, blank=True)
    pronouns = models.TextField(null=True, blank=True)

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
        (PROJECT, 'Project'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links', null=True)
    label = models.CharField(max_length=70)
    url = models.URLField()
    cat = models.CharField(max_length=2, choices=CAT_CHOICES, default=PROJECT)

    def __str__(self):
        return f'{self.url}'


class Progress(models.Model):
    from workshop.models import Workshop

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    page = models.IntegerField(default=0)
    modified = models.DateField(auto_now=True)
