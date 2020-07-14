from django.shortcuts import render, HttpResponse, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import LearnerRegisterForm

# Create your views here.
def profile(request, username=None):
    payload = dict()
    if username:
        payload['user'] = get_object_or_404(User, username=username)
    return render(request, 'learner/profile.html', payload)



def register(request):
    if request.method == 'POST':
        form = LearnerRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You can log in below.')
            return redirect('login')
    else:
        form = LearnerRegisterForm()
    return render(request, 'learner/register.html', {'form': form})