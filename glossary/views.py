from django.shortcuts import render, get_object_or_404
from .models import Term
from lesson.models import Lesson

def build_nav():
    return {'all_terms': Term.objects.all()}

def term(request, slug=None):
    payload = build_nav()
    payload['term'] = Term.objects.filter(slug=slug).last()
    payload['lessons_with_term'] = Lesson.objects.filter(text__contains=f' {payload["term"]} ')
    return render(request, 'glossary/term.html', payload)

def index(request):
    payload = build_nav()
    import random
    payload['random_items'] = []
    if payload['all_terms'].count() > 4:
        payload['random_items'] = random.sample(list(payload['all_terms']), 4)
    return render(request, 'glossary/index.html', payload)