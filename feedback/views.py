from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from lesson.models import Lesson
from .forms import IssueForm


def index(request):
  return redirect('website:index')


def _close_or_redirect(request, username = None):
    if request.GET.get('close') == 'true':
        return HttpResponse('''Thank you for your feedback, ''' + username + '''. We will follow up with you shortly.<br /><br />This window will close in three seconds.

                                <script>
                                    const delay = ms => new Promise(res => setTimeout(res, ms));
                                    const close = async () => {
                                        await delay(3000);
                                        window.close();
                                    };
                                    close();
                                </script>''')
    else:
        messages.info(request, f'Thank you for your feedback, {username}. We will follow up with you shortly.')
        return redirect('website:index')


class Feedback(LoginRequiredMixin, View):
    form = IssueForm()

    def get(self, request, feedback_type, pk=None):
        payload = {'feedback_type': feedback_type}
        if feedback_type == "lesson":
            lesson = get_object_or_404(Lesson, pk=pk)
            payload['lesson'] = lesson
        elif feedback_type == "website":
            pass
        else:
            return HttpResponse('''The requested feedback type (''' + feedback_type + ''') does not exist.''')
        payload['form'] = self.form
        return render(request, 'feedback/feedback_popup.html', payload)

    def post(self, request, feedback_type, pk=None):
        self.form = IssueForm(request.POST)

        if self.form.is_valid():
            feedback = self.form.save(commit=False)
            feedback.user = request.user
            feedback.open = True

            if feedback_type == "lesson":
                feedback.lesson = lesson
                feedback.workshop = lesson.workshop
            elif feedback_type == "website":
                feedback.website = True

            feedback.save()

            return _close_or_redirect(request, username = feedback.user.username)
