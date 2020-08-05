from django.shortcuts import render, get_object_or_404
from .models import Term
from lesson.models import Lesson

def term(request, slug=None):
    obj = Term.objects.filter(slug=slug).last()
    lessons_with_term = Lesson.objects.filter(text__contains=f' {obj.term} ')
    return render(request, 'glossary/term.html', {'term': obj, 'lessons_with_term': lessons_with_term})

def index(request):
    terms = Term.objects.all()
    return render(request, 'glossary/index.html', {'terms': terms})