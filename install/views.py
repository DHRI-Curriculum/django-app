from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import Instruction

def index(request):
    instructions = Instruction.objects.all()
    return render(request, 'install/index.html', {'instructions': instructions})

def installation(request, slug=None):
    installation = get_object_or_404(Instruction, slug=slug)
    return render(request, 'install/installation.html', {'installation': installation})

def checklist(request, slug=None):
    return HttpResponse(f'checklist for {slug}')