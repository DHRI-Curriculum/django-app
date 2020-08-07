from django import forms
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from lesson.models import Lesson
from .forms import IssueForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@ensure_csrf_cookie
def index(request):
  # page = Page.objects.filter(is_homepage=True).last()
  return render(request, 'feedback/index.html', {})


def _close_or_redirect(request, username = None):
    if request.GET.get('close') == 'true':
        return HttpResponse('''
        Thank you for your feedback, ''' + username + '''. We will follow up with you shortly.<br /><br />This window will close in three seconds.

        <script>
            const delay = ms => new Promise(res => setTimeout(res, ms));
            const close = async () => {
                await delay(3000);
                window.close();
            };
            close();
        </script>
        ''')
    else:
        messages.info(request, f'Thank you for your feedback, {username}. We will follow up with you shortly.')
        return redirect('website:index')


@login_required()
def feedback_popup(request, feedback_type, pk=None):

    form = IssueForm()
    lesson = None
    payload = {'feedback_type': feedback_type}

    if feedback_type == "lesson":
        lesson = get_object_or_404(Lesson, pk=pk)
        payload['lesson'] = lesson
    elif feedback_type == "website":
        pass
    else:
        return HttpResponse('''The requested feedback type (''' + feedback_type + ''') does not exist.''')

    if request.method == "POST":
        form = IssueForm(request.POST)

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.open = True

            if feedback_type == "lesson":
                feedback.lesson = lesson
                feedback.workshop = lesson.workshop
            elif feedback_type == "website":
                feedback.website = True

            feedback.save()

            return _close_or_redirect(request, username = feedback.user.username)

    payload['form'] = form

    return render(request, 'feedback/feedback_popup.html', payload)
