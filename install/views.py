from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import Instruction

def index(request):
    return HttpResponse('index for install')

def installation(request, slug=None):
    obj = get_object_or_404(Instruction, slug=slug)
    return HttpResponse(f'''
    {obj.software.software}
    {obj.software.operating_system}r
    ''')

def checklist(request, slug=None):
    return HttpResponse(f'checklist for {slug}')