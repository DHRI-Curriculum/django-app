from django.contrib import admin
from .models import Software, Screenshot, Step, Instruction

admin.site.register(Software)
# admin.site.register(Screenshot)
admin.site.register(Step)
admin.site.register(Instruction)

class ScreenshotAdmin(admin.ModelAdmin):
    pass # exclude = ('gh_name',)

admin.site.register(Screenshot, ScreenshotAdmin)