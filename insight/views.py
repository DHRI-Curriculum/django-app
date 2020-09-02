from django.shortcuts import render, HttpResponse


def index(request):
    return HttpResponse('index')

def insight(request, slug=None):
    return HttpResponse(f'insight for {slug}')