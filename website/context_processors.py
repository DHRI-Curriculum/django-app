from workshop.models import Workshop
from website.models import Page
from django.contrib.auth.models import User, Group
from learner.models import Profile
from backend.dhri_settings import VERSION
from pathlib import Path


instructor = Group.objects.get(name='Instructor')


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


def add_to_all_contexts(request):
    context_data = dict()

    context_data['website'] = dict()
    context_data['version'] = VERSION
    context_data['website']['workshops'] = Workshop.objects.all()
    context_data['website']['pages'] = Page.objects.all()
    if request.user.is_staff:
        context_data['website']['instructor_requests'] = get_pending_requests()

    context_data['is_instructor'] = instructor in request.user.groups.all()

    return context_data