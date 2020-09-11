from django.shortcuts import render, get_object_or_404
from .models import Term
from lesson.models import Lesson
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
import random


class Index(ListView):
    model = Term
    template_name = 'glossary/index.html'
    context_object_name = 'all_terms'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['random_items'] = []
        if self.model.objects.count() > 4:
            context['random_items'] = random.sample(list(self.model.objects.all()), 4)
        return context


class TermDetail(DetailView):
    model = Term
    template_name = 'glossary/term.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lessons_with_term'] = Lesson.objects.filter(terms=self.get_object())
        context['all_terms'] = self.model.objects.all()
        return context