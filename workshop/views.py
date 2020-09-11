from django.shortcuts import render, HttpResponse, get_object_or_404
from django.core.paginator import Paginator
from workshop.models import Workshop, Collaboration, Blurb
from lesson.models import Lesson
from learner.models import Profile
from django.conf import settings
from django.views.generic.detail import DetailView


class FrontmatterView(DetailView):
  model = Workshop
  template_name = 'workshop/frontmatter.html'

  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      self.request.session.set_expiry(0) # expires at browser close
      context['has_visited'] = self.has_visited() # TODO: make sure it works
      context['user_favorited'] = self.has_favorited()
      context['num_terms'], context['all_terms'] = self.get_all_terms()
      context['frontmatter'] = self.get_object().frontmatter
      context['learning_objectives'] = [x.label.replace('<p>', '').replace('</p>', '') for x in context['frontmatter'].learning_objectives.all()]
      context['default_user_image'] = settings.MEDIA_URL + Profile.image.field.default

      context['all_collaborators'] = Collaboration.objects.filter(frontmatter=context['frontmatter']).order_by('contributor__last_name')
      context['current_collaborators'] = context['all_collaborators'].filter(current=True).order_by('contributor__last_name')
      context['past_collaborators'] = context['all_collaborators'].filter(current=False).order_by('contributor__last_name')
      context['current_authors'] = context['current_collaborators'].filter(role='Au').order_by('contributor__last_name')
      context['current_editors'] = context['current_collaborators'].filter(role='Ed').order_by('contributor__last_name')
      context['current_reviewers'] = context['current_collaborators'].filter(role='Re').order_by('contributor__last_name')
      context['past_authors'] = context['past_collaborators'].filter(role='Au').order_by('contributor__last_name')
      context['past_editors'] = context['past_collaborators'].filter(role='Ed').order_by('contributor__last_name')
      context['past_reviewers'] = context['past_collaborators'].filter(role='Re').order_by('contributor__last_name')

      context['blurbs'] = Blurb.objects.filter(workshop=context['workshop']).order_by('user__last_name')

      return context

  def has_visited(self):
    if not self.request.session.get('has_visited', False):
      self.get_object().views += 1
      self.get_object().save()
      self.request.session['has_visited'] = True
      return True
    return True

  def has_favorited(self):
    if self.request.user.is_authenticated:
      if self.get_object() in self.request.user.profile.favorites.all(): return True
    return False

  def get_all_terms(self):
    _ = list()
    for lesson in self.get_object().lessons.all():
      _.extend(list(lesson.terms.all()))
    return(len(_), _)


class PraxisView(DetailView):
  model = Workshop
  template_name = 'workshop/praxis.html'

  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['lessons'] = self.get_object().lessons.all()
      context['praxis'] = self.get_object().praxis
      context['frontmatter'] = self.get_object().frontmatter
      return context


class LessonView(DetailView):
  model = Lesson
  template_name = 'lesson/lesson.html'

  def get_object(self):
    workshop = get_object_or_404(Workshop, slug=self.kwargs.get('slug'))

    try:
      self.lessons
    except:
      self.lessons = Lesson.objects.filter(workshop=workshop)

    self.paginator = Paginator(self.lessons, 1)
    self.page_number = self.request.GET.get('page')

    try:
      self.page_number = int(self.page_number)
    except TypeError:
      pass

    if not self.page_number: self.page_number = 1

    self.page_obj = self.paginator.get_page(self.page_number)
    self.percentage = round(self.page_number / self.paginator.num_pages * 100)

    return self.page_obj.object_list[0]

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['workshop'] = get_object_or_404(Workshop, slug=self.kwargs.get('slug'))
    context['paginator'] = self.paginator
    context['page_obj'] = self.page_obj
    context['percentage'] = self.percentage
    context['lessons'] = self.lessons
    return context