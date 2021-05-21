from django.contrib.auth.models import User, Group
from learner.models import Profile
from workshop.models import Workshop
from install.models import Instructions
from insight.models import Insight
from backend.settings import VERSION
from pathlib import Path


try:
    instructor = Group.objects.get(name='Instructor')
except:
    instructor = []


def get_pending_requests():
    pending_requests = list()
    all_pending_requests = Profile.objects.filter(instructor_requested=True)
    for profile in all_pending_requests:
        if not instructor in profile.user.groups.all():
            pending_requests.append(profile)
        else:
            profile.instructor_requested = False
            profile.save()
    return pending_requests


def get_standard_os_slug(request):
    if 'mac' in request.META.get('HTTP_USER_AGENT', '').lower():
        return 'macos'
    elif 'windows' in request.META.get('HTTP_USER_AGENT', '').lower():
        return 'windows'
    
    return ''


def add_to_all_contexts(request):
    context_data = dict()

    context_data['is_home'] = request.get_full_path() == '/'
    context_data['all_workshops'] = Workshop.objects.all()
    context_data['all_installs'] = Instructions.objects.all()
    context_data['all_insights'] = Insight.objects.all()
    context_data['website'] = dict()
    context_data['version'] = VERSION
    context_data['standard_os_slug'] = get_standard_os_slug(request)
    if request.user.is_staff:
        context_data['website']['instructor_requests'] = get_pending_requests()

    context_data['is_instructor'] = instructor in request.user.groups.all()

    return context_data

