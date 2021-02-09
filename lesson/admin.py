from django.contrib import admin
from .models import Lesson, Challenge, Solution, LessonImage

admin.site.register(Lesson)
admin.site.register(LessonImage)
admin.site.register(Challenge)
admin.site.register(Solution)