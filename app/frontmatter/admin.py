from django.contrib import admin
from .models import Frontmatter, Reading, Project, Resource, Contributor

admin.site.register(Frontmatter)
admin.site.register(Reading)
admin.site.register(Project)
admin.site.register(Resource)
admin.site.register(Contributor)