from django.contrib import admin
from .models import Insight, Section, OperatingSystemSpecificSection

admin.site.register(Insight)
admin.site.register(Section)
admin.site.register(OperatingSystemSpecificSection)