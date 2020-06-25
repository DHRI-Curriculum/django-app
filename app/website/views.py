from django.shortcuts import render, get_object_or_404
from .models import Page

def index(request):
  print('index!')
  page = Page.objects.filter(is_homepage=True).last()
  return render(request, 'website/index.html', {'page': page})

def page(request, page_slug):
  print('page!')
  page = get_object_or_404(Page, slug=page_slug)
  return render(request, 'website/index.html', {'page': page})