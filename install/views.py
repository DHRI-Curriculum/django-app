from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import Instruction

def get_installation_menu_items():
    all_instructions = Instruction.objects.all()
    per_software, per_os = dict(), dict()
    for x in all_instructions:
        if not x.software.software in per_software: per_software[x.software.software] = list()
        per_software[x.software.software].append(x)

        if not x.software.operating_system in per_os: per_os[x.software.operating_system] = list()
        per_os[x.software.operating_system].append(x)
    return {'all_instructions': all_instructions, 'per_software': per_software, 'per_os': per_os}

def index(request):
    payload = get_installation_menu_items()
    return render(request, 'install/index.html', payload)

def installation(request, slug=None):
    payload = get_installation_menu_items()
    payload['instruction'] = get_object_or_404(Instruction, slug=slug)
    return render(request, 'install/installation.html', payload)

def checklist(request, slug=None):
    return HttpResponse(f'checklist for {slug}')