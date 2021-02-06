from django.contrib import admin
from .models import Reading, Project, Tutorial
# from .models import Resource

admin.site.register(Reading)
admin.site.register(Project)
# admin.site.register(Resource)
admin.site.register(Tutorial)
