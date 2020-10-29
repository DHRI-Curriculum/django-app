from django.contrib import admin
from .models import Snippet


class SnippetAdmin(admin.ModelAdmin):
    list_display = ("identifier", "admin_get_snippet")

    def admin_get_snippet(self, obj):
        if len(obj.snippet) > 200:
            return obj.snippet[:200] + '...'
        return obj.snippet
    admin_get_snippet.short_description = u'Snippet'


admin.site.register(Snippet, SnippetAdmin)
