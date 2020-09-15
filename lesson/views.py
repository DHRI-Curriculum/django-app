import json

from django.views.generic import View
from django.http import JsonResponse

from .models import Answer

class CheckAnswer(View):

    def post(self, request, *args, **kwargs):
        question_id = request.headers.get('Question')
        answers = request.headers.get('Answers')
        try:
            answers = json.loads(answers)
        except:
            return JsonResponse({'error': 'could not interpret JSON data'})

        correct = dict()

        for answer_id, response in answers.items():
            a = Answer.objects.get(pk=answer_id)
            correct[answer_id] = response == a.is_correct

        return JsonResponse({
            'error': None,
            'question_id': question_id,
            'answers_provided': answers,
            'correct_answers': correct,
            'all_correct': all(x == True for x in correct.values())
        })