from django.shortcuts import render, get_object_or_404
from .models import Term
from lesson.models import Lesson
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
import random





class TermList(ListView):
    model = Term

    def get_slug(self):
        slug = self.kwargs.get('slug')
        if not slug:
            return 'A'
        return slug

    def get_queryset(self):
        slug = self.get_slug()
        return Term.objects.filter(term__istartswith=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slug'] = self.get_slug()
        return context


class TermDetail(DetailView):
    model = Term
    template_name = 'glossary/term.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lessons_with_term'] = Lesson.objects.filter(terms=self.get_object())
        return context