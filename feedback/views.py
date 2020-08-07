from django import forms
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from lesson.models import Lesson
from .forms import IssueForm
from django.contrib import messages

@ensure_csrf_cookie
def index(request):
  # page = Page.objects.filter(is_homepage=True).last()
  return render(request, 'feedback/index.html', {})

def lesson_popup(request, lesson_id):
    if request.user.is_authenticated == False:
        return HttpResponse("You have to be logged in to use this feature.")

    lesson = get_object_or_404(Lesson, pk=lesson_id)

    if request.method == "POST":
        form = IssueForm(request.POST)

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.lesson = lesson
            feedback.workshop = lesson.workshop
            feedback.user = request.user
            feedback.open = True
            feedback.save()
            username = feedback.user

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

    else:
        form = IssueForm()

    return render(request, 'feedback/lesson_popup.html', {'lesson': lesson, 'form': form})

def thank_you(request):
    return render(request, 'feedback/thank_you.html', {'post': request.POST})