from django.shortcuts import render, HttpResponse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Insight


class Index(ListView):
    model = Insight


class InsightDetail(DetailView):
    model = Insight

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = self.model.objects.all()
        return context