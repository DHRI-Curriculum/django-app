from django.shortcuts import render, HttpResponse, get_object_or_404
from django.core.exceptions import MultipleObjectsReturned
from django.core.paginator import Paginator
# from website.models import Page
from workshop.models import Workshop
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
  lessons = Lesson.objects.filter(workshop=obj)
  praxis = obj.praxis
  return render(request, 'workshop/praxis.html', {'workshop': obj, 'frontmatter': frontmatter, 'praxis': praxis, 'lessons': lessons})


def lesson(request, slug=None, lesson_id=None):
  _, obj = _flexible_get(Workshop, slug)
  lessons = Lesson.objects.filter(workshop=obj)
  paginator = Paginator(lessons, 1)

  page_number = request.GET.get('page')

  try:
    page_number = int(page_number)
  except TypeError:
    pass

  if not page_number: page_number = 1

  page_obj = paginator.get_page(page_number)

  percentage = round(page_number / paginator.num_pages * 100)

  lesson = page_obj.object_list[0]
  return render(request, 'lesson/lesson.html', {'workshop': obj, 'lessons': lessons, 'lesson': lesson, 'page_obj': page_obj, 'percentage': percentage})
