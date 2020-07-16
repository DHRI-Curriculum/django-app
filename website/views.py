from django.shortcuts import render, get_object_or_404
from .models import Page
from workshop.models import Workshop
from library.models import Project, Reading, Resource, Tutorial
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def index(request):
  page = Page.objects.filter(is_homepage=True).last()
  return render(request, 'website/index.html', {'page': page})

@ensure_csrf_cookie
def page(request, page_slug):
  payload = dict()

  page = get_object_or_404(Page, slug=page_slug)
  payload['page'] = page

  if page.template == Page.Template.WORKSHOP_LIST:
    payload['workshops'] = Workshop.objects.all()

  if page.template == Page.Template.LIBRARY_LIST:
    payload['projects'] = Project.objects.all().order_by('title')[:3]
    payload['readings'] = Reading.objects.all().order_by('title')[:3]
    payload['resources'] = Resource.objects.all().order_by('title')[:3]
    payload['tutorials'] = Tutorial.objects.all().order_by('label')[:3]

  return render(request, page.template, payload)