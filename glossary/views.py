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
        allowed = [x.lower() for x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
        letter = self.get_slug()
        extra = {}
        for t in Term.objects.all().order_by('term'):
            if not t.term[0].lower() in allowed:
                done = False
                for i in range(2,len(t.term)):
                    if done: continue
                    if t.term[i-1:i].lower() in allowed:
                        if not t.term[i-1:i] in extra:
                            extra[t.term[i-1:i]] = []
                        extra[t.term[i-1:i]].append(t.term)
                        done = True
        
        if letter in extra.keys():
            for term in extra[letter]:
                objects = Term.objects.filter(term=term)
        try:
            return objects | Term.objects.filter(term__istartswith=letter)
        except:
            return Term.objects.filter(term__istartswith=letter)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slug'] = self.get_slug()
        if self.model.objects.count() > 4:
            context['random_items'] = random.sample(list(self.model.objects.all()), 4)
        return context


class TermDetail(DetailView):
    model = Term

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_slug'] = self.object.term[:1].upper()
        return context