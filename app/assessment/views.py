from django.shortcuts import render, HttpResponse, get_object_or_404
from django.views import View
from .models import Question
from .forms import TestForm


class Test(View):

    form_class = TestForm
    initial_values = {}

    def get(self, request, question_id, *args, **kwargs):
        form = self.form_class(initial=self.initial_values)

        question = get_object_or_404(Question, pk=question_id)
        
        if question.question_type.label.lower() in ['multi-choice', 'radio', 'checkbox', 'select']:
            question.form_setting = "values"
        return render(request, 'assessment/test.html', {'question': question, 'form': form})

        #return HttpResponse("Nothing to see here.")

    def post(self, request, question_id, *args, **kwargs):
        form = self.form_class(request.POST)
        return HttpResponse(f"POST received for {question_id}: {request.POST}. args: {args}. kwargs: {kwargs}")



def index(request):
    return HttpResponse("Nothing to see here.")