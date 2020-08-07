from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .tokens import account_activation_token
from .models import Profile
from django.http import JsonResponse, HttpResponseForbidden
from workshop.models import Workshop
from django.views.decorators.csrf import csrf_protect

def profile(request, username=None):
    payload = dict()

    if username and request.user.username == username:
        payload['is_me'] = True
    elif not username:
        payload['is_me'] = True
    else:
        payload['is_me'] = False

    if payload['is_me']:
        instructor = Group.objects.get(name='Instructor')
        # payload['is_instructor'] = instructor in request.user.groups.all()
        payload['user'] = request.user
        payload['favorites'] = request.user.profile.favorites.all()
        payload['instructor_requested'] = request.user.profile.instructor_requested
    else:
        payload['user'] = get_object_or_404(User, username=username)
        payload['favorites'] = payload['user'].profile.favorites.all()
    return render(request, 'learner/profile.html', payload)


def register(request):
    from .forms import LearnerRegisterForm
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode
    from django.template.loader import render_to_string
    from django.core.mail import EmailMessage
    from django.contrib.sites.shortcuts import get_current_site

    if request.method == 'POST':
        form = LearnerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            username = form.cleaned_data.get('username')
            messages.info(request, f'Account created for {username}. You have to click the confirmation link in the email in order to activate your account.')

            message = render_to_string('learner/new_acc_email.html', {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage('Activate your account', message, to=[to_email])
            email.send()

            return redirect('login')
    else:
        form = LearnerRegisterForm()
    return render(request, 'learner/register.html', {'form': form})



def activate(request, uidb64='', token=''):
    from django.utils.http import urlsafe_base64_decode
    from django.contrib.auth import login
    from django.utils.encoding import force_text

    uid = force_text(urlsafe_base64_decode(uidb64))
    try:
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, f'Thank you for your email confirmation, {user.username}. You have been logged in automatically.')
        return redirect('website:index')
    else:
        return HttpResponse('Activation link is invalid!')


@csrf_protect
def favorite(request):
    if not request.user.is_authenticated: # TODO: Does not seem to work
        return HttpResponseForbidden()

    workshop = request.headers.get('workshop')
    obj = get_object_or_404(Workshop, slug=workshop)

    removed, added = False, False
    if obj in request.user.profile.favorites.all():
        request.user.profile.favorites.remove(obj)
        print(obj, "removed as favorite")
        removed = True
    else:
        request.user.profile.favorites.add(obj)
        print(obj, "added as favorite")
        added = True

    output_data = {'workshop': obj.name, 'success': True, 'added': added, 'removed': removed}

    return JsonResponse(output_data)


@csrf_protect
def instructor_request(request):
    if not request.user.is_authenticated: # TODO: Does not seem to work
        return HttpResponseForbidden()

    request.user.profile.instructor_requested = True
    request.user.profile.save()

    output_data = {'success': True}

    return JsonResponse(output_data)


def get_pending_requests():
    instructor = Group.objects.get(name='Instructor')
    pending_requests = list()
    all_pending_requests = Profile.objects.filter(instructor_requested=True)
    for profile in all_pending_requests:
        if not instructor in profile.user.groups.all():
            pending_requests.append(profile)
        else:
            profile.instructor_requested = False
            profile.save()
    return pending_requests


def instructor_requests(request):
    if request.method == "GET":
        if not request.user.is_superuser:
            return HttpResponseForbidden()

        pending_requests = get_pending_requests()

        return render(request, 'learner/requests.html', {'pending_requests': pending_requests})
    else:
        instructor = Group.objects.get(name='Instructor')
        username = request.headers.get('username')
        print(username)
        user = get_object_or_404(User, username=username)

        user.groups.add(instructor)
        user.profile.instructor_requested = False
        user.profile.save()

        output_data = {'success': True}
        return JsonResponse(output_data)