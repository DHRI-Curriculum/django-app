from django.shortcuts import render, HttpResponse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Instruction, Software
from django.urls import reverse


def get_installation_menu_items():
    all_instructions = Instruction.objects.all().order_by(
        'software__software', 'software__operating_system'
    )
    per_software, per_os = dict(), dict()
    for x in all_instructions:
        if not x.software.software in per_software: per_software[x.software.software] = list()
        per_software[x.software.software].append(x)

        if not x.software.operating_system in per_os: per_os[x.software.operating_system] = list()
        per_os[x.software.operating_system].append(x)
    return {'per_software': per_software, 'per_os': per_os}


class Index(ListView):
    model = Instruction
    template_name = 'install/index.html'
    context_object_name = 'all_instructions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {**context, **get_installation_menu_items()}
        return context


class Detail(DetailView):
    model = Instruction
    template_name = 'install/installation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {**context, **get_installation_menu_items()}

        other_os, context['other_os_slug'] = None, None
        if 'macos' in context['instruction'].software.operating_system.lower(): other_os = 'Windows'
        elif 'windows' in context['instruction'].software.operating_system.lower(): other_os = 'macOS'

        if other_os:
            current_software = context['instruction'].software.software
            context['other_os_slug'] = Software.objects.get(software=current_software, operating_system=other_os).instructions.all().last().slug

        return context