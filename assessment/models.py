from django.db import models
from adminsortable.models import SortableMixin
from adminsortable.fields import SortableForeignKey




QUESTION_TYPE_CHOICES = [
    ('radio', 'Multiple choice (checkbox)'),
    ('select', 'Dropdown menu'),
    ('checkbox', 'Multiple choice (checkbox)'),
    ('text', 'Textfield')
]



class QuestionType(models.Model):
    label = models.TextField(max_length=500)

    def __str__(self):
        return f'{self.label}'


class Question(SortableMixin):
    label = models.TextField(max_length=500)
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.label}'


class Answer(SortableMixin):
    label = models.TextField(max_length=500)
    order = models.PositiveSmallIntegerField(default=0, editable=False, db_index=True)
    question = SortableForeignKey(Question, on_delete=models.CASCADE, related_name="answer")
    is_correct_answer = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.label}'