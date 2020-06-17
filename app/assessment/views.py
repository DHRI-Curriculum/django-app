from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import Question
from .forms import TestForm


def test(request, question_id):
    form = TestForm()
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'assessment/test.html', {'question': question, 'form': form})


def index(request):
    return HttpResponse("Nothing to see here.")