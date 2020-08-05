from django.shortcuts import render, get_object_or_404
from .models import Term

def term(request, slug=None):
    obj = Term.objects.filter(slug=slug).last()
    return render(request, 'glossary/term.html', {'term': obj})

def index(request):
    terms = Term.objects.all()
    return render(request, 'glossary/index.html', {'terms': terms})