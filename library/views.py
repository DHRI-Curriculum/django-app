from django.shortcuts import render
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import ListView


from .models import Reading, Tutorial, Project
# from .models import Resource


payload = dict()


class Index(ListView):
    models = [Reading, Tutorial, Project]
    # models.append(Resource)
    template_name = 'library/index.html'

    def get_queryset(self):
        _ = dict()
        for model in self.models:
            _[model._meta.verbose_name_plural] = model.objects.all()
        return(_)

def lazyload_projects(request):
    page = request.headers.get('page')
    projects = Project.objects.all().order_by('title')
    paginator = Paginator(projects, 3)
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(2)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    projects_html = loader.render_to_string(
        'library/fragments/projects.html',
        {'projects': projects}
    )
    output_data = { 'html': projects_html, 'has_next': projects.has_next() }
    return JsonResponse(output_data)

def lazyload_readings(request):
    page = request.headers.get('page')
    readings = Reading.objects.all().order_by('title')
    paginator = Paginator(readings, 3)
    try:
        readings = paginator.page(page)
    except PageNotAnInteger:
        readings = paginator.page(2)
    except EmptyPage:
        readings = paginator.page(paginator.num_pages)

    html = loader.render_to_string(
        'library/fragments/readings.html',
        {'readings': readings}
    )
    output_data = { 'html': html, 'has_next': readings.has_next() }
    return JsonResponse(output_data)

'''
def lazyload_resources(request):
    page = request.headers.get('page')
    resources = Resource.objects.all().order_by('title')
    paginator = Paginator(resources, 3)
    try:
        resources = paginator.page(page)
    except PageNotAnInteger:
        resources = paginator.page(2)
    except EmptyPage:
        resources = paginator.page(paginator.num_pages)

    html = loader.render_to_string(
        'library/fragments/resources.html',
        {'resources': resources}
    )
    output_data = { 'html': html, 'has_next': resources.has_next() }
    return JsonResponse(output_data)
'''

def lazyload_tutorials(request):
    page = request.headers.get('page')
    tutorials = Tutorial.objects.all().order_by('label')
    paginator = Paginator(tutorials, 3)
    try:
        tutorials = paginator.page(page)
    except PageNotAnInteger:
        tutorials = paginator.page(2)
    except EmptyPage:
        tutorials = paginator.page(paginator.num_pages)

    html = loader.render_to_string(
        'library/fragments/tutorials.html',
        {'tutorials': tutorials}
    )
    output_data = { 'html': html, 'has_next': tutorials.has_next() }
    return JsonResponse(output_data)



def project_details(request):
    pass