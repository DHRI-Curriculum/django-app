from django.shortcuts import render, get_object_or_404
from .models import Page
from workshop.models import Workshop
from library.models import Project, Reading, Resource, Tutorial
from django.views.decorators.csrf import ensure_csrf_cookie


payload = dict()


@ensure_csrf_cookie
def index(request):
  payload['page'] = Page.objects.filter(is_homepage=True).last()
  return render(request, 'website/index.html', payload)

@ensure_csrf_cookie
def page(request, page_slug):

  payload['page'] = get_object_or_404(Page, slug=page_slug)

  if payload['page'].template == Page.Template.WORKSHOP_LIST:
    payload['workshops'] = Workshop.objects.all()

  if payload['page'].template == Page.Template.LIBRARY_LIST:
    projects = Project.objects.all().order_by('title')
    readings = Reading.objects.all().order_by('title')
    resources = Resource.objects.all().order_by('title')
    tutorials = Tutorial.objects.all().order_by('label')

    payload['projects'] = projects[:3]
    payload['readings'] = readings[:3]
    payload['resources'] = resources[:3]
    payload['tutorials'] = tutorials[:3]

    payload['projects_count'] = projects.count()
    payload['readings_count'] = readings.count()
    payload['resources_count'] = resources.count()
    payload['tutorials_count'] = tutorials.count()

  return render(request, payload['page'].template, payload)