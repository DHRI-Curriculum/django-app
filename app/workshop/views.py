from django.shortcuts import render, HttpResponse, get_object_or_404
from django.core.exceptions import MultipleObjectsReturned
from .models import Workshop
from website.models import Page


def _flexible_get(model=None, slug_or_int=''):
  try:
    int(slug_or_int)
    is_id, is_slug = True, False
  except ValueError:
    is_id, is_slug = False, True
  except TypeError:
    is_id, is_slug = False, False

  if is_slug:
    try:
      multiple = False
      obj = get_object_or_404(model, slug=slug_or_int)
    except MultipleObjectsReturned:
      multiple = True
      obj = model.objects.filter(slug=slug_or_int).last()
    return(multiple, obj)
  elif is_id:
    obj = get_object_or_404(model, pk=slug_or_int)
    return(False, obj)
  else:
    response = f"You have not selected a valid ID for the model {model}."
    return HttpResponse(response, status=500)



def index(request):
  workshops = Workshop.objects.all()
  return render(request, 'workshop/workshop-list.html', {'workshops': workshops})

def frontmatter(request, slug=None):
  _, obj = _flexible_get(Workshop, slug)
  frontmatter = obj.frontmatter
  return render(request, 'workshop/frontmatter.html', {'workshop': obj, 'frontmatter': frontmatter})

def praxis(request, slug=None):
  _, obj = _flexible_get(Workshop, slug)
  frontmatter = obj.frontmatter
  praxis = obj.praxis
  return render(request, 'workshop/praxis.html', {'workshop': obj, 'frontmatter': frontmatter, 'praxis': praxis})

def lesson(request, slug=None, lesson_slug=None):
  _, obj = _flexible_get(Workshop, slug)
  frontmatter = obj.frontmatter
  return render(request, 'lesson/lesson.html', {'workshop': obj, 'frontmatter': frontmatter})