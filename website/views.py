from django.shortcuts import render, get_object_or_404
from .models import Page
from workshop.models import Workshop
from library.models import Project, Reading, Resource, Tutorial
from django.views.generic.detail import DetailView
from django.views.generic import View


class Index(DetailView):
  model = Page
  template_name = 'website/index.html'

  def get_object(self):
    return self.model.objects.filter(is_homepage=True).last()

  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["object_list"] = Workshop.objects.all()
      return context



class PageView(View):
  model = Page

  def get(self, request, **kwargs):
    page = self.get_object()
    context = self.get_context_data()
    return render(request, page.template, context)

  def get_object(self):
    return get_object_or_404(self.model, slug=self.kwargs.get('slug'))

  def get_context_data(self, **kwargs):
    context = dict()
    page = self.get_object()
    if page.template == Page.Template.WORKSHOP_LIST:
      context['workshops'] = Workshop.objects.all()

    if page.template == Page.Template.LIBRARY_LIST:
      context['projects'] = Project.objects.all().order_by('title')[:3]
      context['readings'] = Reading.objects.all().order_by('title')[:3]
      context['resources'] = Resource.objects.all().order_by('title')[:3]
      context['tutorials'] = Tutorial.objects.all().order_by('label')[:3]
      context['projects_count'] = Project.objects.count()
      context['readings_count'] = Reading.objects.count()
      context['resources_count'] = Resource.objects.count()
      context['tutorials_count'] = Tutorial.objects.count()

    return context