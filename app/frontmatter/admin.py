from django.contrib import admin
from .models import Frontmatter, Contributor

admin.site.register(Frontmatter)
admin.site.register(Contributor)