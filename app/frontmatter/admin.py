from django.contrib import admin
from .models import Frontmatter, Literature, Project, Resource, Contributor

admin.site.register(Frontmatter)
admin.site.register(Literature)
admin.site.register(Project)
admin.site.register(Resource)
admin.site.register(Contributor)