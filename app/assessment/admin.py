from django.contrib import admin
from adminsortable.admin import SortableAdmin
from adminsortable.admin import NonSortableParentAdmin, SortableStackedInline
from adminsortable.admin import SortableTabularInline
from .models import Answer, Question, QuestionType


class AnswerInline(SortableTabularInline):
    model = Answer
    extra = 1


class QuestionAdmin(NonSortableParentAdmin):
    inlines = [AnswerInline]


admin.site.register(Answer, SortableAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionType)