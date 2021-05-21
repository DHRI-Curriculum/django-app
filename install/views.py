from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Instructions, Software
from django.shortcuts import get_object_or_404


class SoftwareIndexView(ListView):
    model = Software


class SoftwareView(DetailView):
    model = Software

    context_object_name = 'software'


class OSView(DetailView):
    model = Instructions

    context_object_name = 'instructions'

    def get_object(self):
        return get_object_or_404(
            self.model,
            software__slug=self.kwargs['software_slug'],
            operating_system__slug=self.kwargs['os_slug'],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['software_slug'] = self.kwargs['software_slug']
        context['os_slug'] = self.kwargs['os_slug']
        if 'mac' in context['os_slug']:
            context['other_os_slug'] = 'windows'
        elif 'windows' in context['os_slug']:
            context['other_os_slug'] = 'macos'
        return context
