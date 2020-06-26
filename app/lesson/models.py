from django.db import models
from workshop.models import Workshop

class Lesson(models.Model):
  title = models.CharField(max_length=200)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  workshop = models.OneToOneField(Workshop, on_delete=models.CASCADE)
  text = models.TextField()


class Challenge(models.Model):
  lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE)
  title = models.CharField(max_length=200)
  text = models.TextField()


class Solution(models.Model):
  challenge = models.OneToOneField(Challenge, on_delete=models.CASCADE)
  title = models.CharField(max_length=200)
  text = models.TextField()