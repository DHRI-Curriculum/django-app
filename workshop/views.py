from django.shortcuts import render, HttpResponse, get_object_or_404
from django.core.exceptions import MultipleObjectsReturned
from django.core.paginator import Paginator
from workshop.models import Workshop, Collaboration, Blurb
from lesson.models import Lesson
from learner.models import Profile
from django.conf import settings


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

payload = dict()

def frontmatter(request, slug=None):

  request.session.set_expiry(0) # expires at browser close

  _, payload['workshop'] = _flexible_get(Workshop, slug)

  if not request.session.get('has_visited', False):
    payload['workshop'].views += 1
    payload['workshop'].save()
    request.session['has_visited'] = True

  payload['workshop'].has_visited = request.session.get('has_visited', False)

  payload['user_favorited'] = False
  if request.user.is_authenticated:
    if payload['workshop'] in request.user.profile.favorites.all(): payload['user_favorited'] = True

  payload['lessons'] = Lesson.objects.filter(workshop=payload['workshop'])
  payload['all_terms'] = list()
  for lesson in payload['lessons']:
    payload['all_terms'].extend(list(lesson.terms.all()))
  payload['num_terms'] = len(payload['all_terms'])

  payload['frontmatter'] = payload['workshop'].frontmatter
  payload['learning_objectives'] = [x.label.replace('<p>', '').replace('</p>', '') for x in payload['frontmatter'].learning_objectives.all()]
  payload['default_user_image'] = settings.MEDIA_URL + Profile.image.field.default

  payload['all_collaborators'] = Collaboration.objects.filter(frontmatter=payload['frontmatter']).order_by('contributor__last_name')
  payload['current_collaborators'] = payload['all_collaborators'].filter(current=True).order_by('contributor__last_name')
  payload['past_collaborators'] = payload['all_collaborators'].filter(current=False).order_by('contributor__last_name')
  payload['current_authors'] = payload['current_collaborators'].filter(role='Au').order_by('contributor__last_name')
  payload['current_editors'] = payload['current_collaborators'].filter(role='Ed').order_by('contributor__last_name')
  payload['current_reviewers'] = payload['current_collaborators'].filter(role='Re').order_by('contributor__last_name')
  payload['past_authors'] = payload['past_collaborators'].filter(role='Au').order_by('contributor__last_name')
  payload['past_editors'] = payload['past_collaborators'].filter(role='Ed').order_by('contributor__last_name')
  payload['past_reviewers'] = payload['past_collaborators'].filter(role='Re').order_by('contributor__last_name')

  payload['blurbs'] = Blurb.objects.filter(workshop=payload['workshop']).order_by('user__last_name')
  for blurb in payload['blurbs']:
    print(blurb.user.profile.personal_links())
  return render(request, 'workshop/frontmatter.html', payload)


def praxis(request, slug=None):
  _, payload['workshop'] = _flexible_get(Workshop, slug)
  payload['frontmatter'] = payload['workshop'].frontmatter
  payload['lessons'] = Lesson.objects.filter(workshop=payload['workshop'])
  payload['praxis'] = payload['workshop'].praxis
  return render(request, 'workshop/praxis.html', payload)


def lesson(request, slug=None, lesson_id=None):
  _, payload['workshop'] = _flexible_get(Workshop, slug)
  payload['lessons'] = Lesson.objects.filter(workshop=payload['workshop'])
  paginator = Paginator(payload['lessons'], 1)

  page_number = request.GET.get('page')

  try:
    page_number = int(page_number)
  except TypeError:
    pass

  if not page_number: page_number = 1

  payload['page_obj'] = paginator.get_page(page_number)

  payload['percentage'] = round(page_number / paginator.num_pages * 100)

  payload['lesson'] = payload['page_obj'].object_list[0]
  return render(request, 'lesson/lesson.html', payload)
