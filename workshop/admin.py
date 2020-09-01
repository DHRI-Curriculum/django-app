from django.contrib import admin
from .models import Workshop, Frontmatter, Contributor, Praxis, Collaboration, Blurb

admin.site.register(Workshop)
admin.site.register(Praxis)
admin.site.register(Frontmatter)
admin.site.register(Contributor)
admin.site.register(Collaboration)
admin.site.register(Blurb)