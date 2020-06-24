# from workshop.models import Workshop

from pathlib import Path

def add_to_all_contexts(request):
    context_data = dict()
    # context_data['all_workshops'] = Workshop.objects.all().count()
    return context_data