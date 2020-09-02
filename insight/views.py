from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import Insight


payload = dict()
payload['all_insights'] = Insight.objects.all()


def index(request):
    return render(request, 'insight/index.html', payload)


def insight(request, slug=None):
    payload['insight'] = get_object_or_404(Insight, slug=slug)
    return render(request, 'insight/insight.html', payload)