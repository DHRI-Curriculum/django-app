from django.shortcuts import render, HttpResponse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Instruction, Software
from django.urls import reverse


class Index(ListView):
    model = Instruction

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class Detail(DetailView):
    model = Instruction

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        other_os, context['other_os_slug'] = None, None
        if 'macos' in context['instruction'].software.operating_system.lower(): other_os = 'Windows'
        elif 'windows' in context['instruction'].software.operating_system.lower(): other_os = 'macOS'

        if other_os:
            current_software = context['instruction'].software.software
            context['other_os_slug'] = Software.objects.get(software=current_software, operating_system=other_os).instructions.all().last().slug

        return context