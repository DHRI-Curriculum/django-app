from django.db import models
from adminsortable.models import SortableMixin
from adminsortable.fields import SortableForeignKey




class QuestionType(models.Model):
    label = models.TextField(max_length=500)

    def __str__(self):
        return self.label


class Question(SortableMixin):
    label = models.TextField(max_length=500)
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.label


class Answer(SortableMixin):
    label = models.TextField(max_length=500)
    order = models.PositiveSmallIntegerField(default=0, editable=False, db_index=True)
    question = SortableForeignKey(Question, on_delete=models.CASCADE, related_name="answer")
    is_correct_answer = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.label


"""
class QuestionOrder(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.question} answer #{self.order}"
"""