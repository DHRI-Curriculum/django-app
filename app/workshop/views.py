from django.shortcuts import render, HttpResponse, get_object_or_404
from django.core.exceptions import MultipleObjectsReturned
from django.core.paginator import Paginator
from .models import Workshop
from website.models import Page
from lesson.models import Lesson


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
  request.session.set_expiry(0) # expires at browser close

  _, obj = _flexible_get(Workshop, slug)
  has_visited = request.session.get('has_visited', False)

  if not has_visited:
    obj.views += 1
    obj.save()
    request.session['has_visited'] = True

  obj.has_visited = request.session.get('has_visited', False)

  lessons = Lesson.objects.filter(workshop=obj)
  frontmatter = obj.frontmatter
  return render(request, 'workshop/frontmatter.html', {'workshop': obj, 'frontmatter': frontmatter, 'lessons': lessons})


def praxis(request, slug=None):
  _, obj = _flexible_get(Workshop, slug)
  frontmatter = obj.frontmatter
  praxis = obj.praxis
  return render(request, 'workshop/praxis.html', {'workshop': obj, 'frontmatter': frontmatter, 'praxis': praxis})

'''
def lesson(request, slug=None, lesson_id=None):
  _, obj = _flexible_get(Workshop, slug)
  lessons = Lesson.objects.filter(workshop=obj)
  lesson = get_object_or_404(Lesson, pk=lesson_id)
  next_lesson = lesson.next
  return render(request, 'lesson/lesson.html', {'workshop': obj, 'frontmatter': frontmatter, 'lessons': lessons, 'lesson': lesson, 'next_lesson': next_lesson})
'''


def lesson(request, slug=None, lesson_id=None):
  _, obj = _flexible_get(Workshop, slug)
  lessons = Lesson.objects.filter(workshop=obj)
  paginator = Paginator(lessons, 1)

  page_number = request.GET.get('page')

  try:
    page_number = int(request.GET.get('page'))
  except: # TODO: should make this exception explicit
    page_number = request.GET.get('page')

  if not page_number: page_number = 1

  page_obj = paginator.get_page(page_number)

  percentage = round(page_number / paginator.num_pages * 100)

  lesson = page_obj.object_list[0]
  return render(request, 'lesson/lesson.html', {'workshop': obj, 'lessons': lessons, 'lesson': lesson, 'page_obj': page_obj, 'percentage': percentage})
