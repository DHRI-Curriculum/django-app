from django.shortcuts import render, HttpResponse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Insight


class Index(ListView):
    model = Insight
    template_name = 'insight/index.html'
    context_object_name = 'all_insights'


class InsightDetail(DetailView):
    model = Insight
    template_name = 'insight/insight.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_insights'] = self.model.objects.all()
        return context