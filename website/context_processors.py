from workshop.models import Workshop
from website.models import Page

from pathlib import Path

def add_to_all_contexts(request):
    context_data = dict()

    context_data['website'] = dict()
    context_data['website']['workshops'] = Workshop.objects.all()
    context_data['website']['pages'] = Page.objects.all()

    return context_data