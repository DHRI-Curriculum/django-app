from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .tokens import account_activation_token
from .models import Profile
from django.http import JsonResponse, HttpResponseForbidden
from workshop.models import Workshop, Collaboration, Contributor
from django.views.decorators.csrf import csrf_protect
from django.views.generic.detail import DetailView
from django.views.generic import View
from django.template.loader import get_template


class Detail(DetailView):
    model = Profile
    template_name = 'learner/profile.html'

    def get_user_object(self):
        try:
            return self.user_obj
        except:
            self.user_obj = get_object_or_404(User, username=self.kwargs.get('username'))
            return self.user_obj

    def get_contributor_object(self):
        try:
            return self.contributor_obj
        except:
            try:
                self.contributor_obj = Contributor.objects.get(profile=self.get_user_object().profile)
                return self.contributor_obj
            except:
                return None

    def get_object(self):
        user_obj = self.get_user_object()
        return user_obj.profile

    def is_me(self):
        user_obj = self.get_user_object()
        return user_obj == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_me'] = self.is_me()
        if context['is_me']:
            context['user'] = self.request.user
        else:
            context['user'] = self.get_user_object()

        context['contributor'] = self.get_contributor_object()
        context['is_instructor'] = Group.objects.get(name='Instructor') in self.request.user.groups.all()

        return context


from .forms import LearnerRegisterForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes

class Register(View):

    form = LearnerRegisterForm()

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('website:index')
        return render(request, 'learner/register.html', {'form': self.form})

    def post(self, request):
        self.form = LearnerRegisterForm(request.POST)

        if self.form.is_valid():
            user = self.form.save(commit=False)
            user.is_active = False
            user.save()
            username = self.form.cleaned_data.get('username')
            messages.info(request, f'Account created for {username}. You have to click the confirmation link in the email in order to activate your account.')

            context = {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            }
            text_message = get_template('learner/fragments/email/new_acc_email.txt').render(context)
            html_message = get_template('learner/fragments/email/new_acc_email.html').render(context)
            to_email = self.form.cleaned_data.get('email')
            email = EmailMultiAlternatives('Activate your account', text_message, 'Digital Humanities Research Institute <info@dhinstitutes.org>', [to_email])
            email.attach_alternative(html_message, "text/html")
            email.send()

            return redirect('login')
        else:
            return self.get(request=request)


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
        #print(obj, "removed as favorite")
        removed = True
    else:
        request.user.profile.favorites.add(obj)
        #print(obj, "added as favorite")
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


from django.views.generic import View

class InstructorRequests(View):

    def post(self, request, *args, **kwargs):
        instructor = Group.objects.get(name='Instructor')
        user = get_object_or_404(User, username=request.user.username)

        user.groups.add(instructor)
        user.profile.instructor_requested = False
        user.profile.save()

        output_data = {'success': True}
        return JsonResponse(output_data)

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden()

        pending_requests = get_pending_requests()

        return render(request, 'learner/requests.html', {'pending_requests': pending_requests})