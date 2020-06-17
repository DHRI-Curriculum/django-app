from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import Question


def test(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'assessment/test.html', {'question': question})


def index(request):
    return HttpResponse("Nothing to see here.")