from django.shortcuts import render, HttpResponse, get_object_or_404
from django.core.exceptions import MultipleObjectsReturned
from .models import Workshop

def index(request):
  workshops = Workshop.objects.all()
  return render(request, 'workshop/index.html', {'workshops': workshops})

def detail(request, slug=None):
  try:
    int(slug)
    is_id, is_slug = True, False
  except ValueError:
    is_id, is_slug = False, True
  except TypeError:
    is_id, is_slug = False, False

  if is_slug:
    try:
      multiple = False
      obj = get_object_or_404(Workshop, slug=slug)
    except MultipleObjectsReturned:
      multiple = True
      obj = Workshop.objects.filter(slug=slug).last()
    response = f"You have selected workshop slug {obj.slug} ({obj.name})."
    if multiple:
      response += f"<br />This workshop exists multiple times in the database. The latest one is displayed."
  elif is_id:
    obj = get_object_or_404(Workshop, pk=slug)
    response = f"You have selected workshop slug {obj.slug} ({obj.name})."
  else:
    response = f"You have not selected a workshop ID."
  # return HttpResponse(response)
  return render(request, 'workshop/detail.html', {'workshop': obj})