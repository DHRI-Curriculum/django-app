from django.shortcuts import render, HttpResponse, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .tokens import account_activation_token

def profile(request, username=None):
    payload = dict()
    if username:
        payload['user'] = get_object_or_404(User, username=username)
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
