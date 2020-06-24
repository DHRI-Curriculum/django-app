from workshop.models import Workshop

from pathlib import Path

def add_to_all_contexts(request):
    context_data = dict()

    context_data['footer'] = dict()
    context_data['footer']['workshops'] = Workshop.objects.all()

    return context_data