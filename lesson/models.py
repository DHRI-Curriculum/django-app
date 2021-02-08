from django.db import models
from workshop.models import Workshop
from glossary.models import Term
from backend.mixins import CurlyQuotesMixin


class Lesson(CurlyQuotesMixin, models.Model):
    curly_fields = ['text']

    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    workshop = models.ForeignKey(
        Workshop, on_delete=models.CASCADE, related_name='lessons')
    text = models.TextField()
    terms = models.ManyToManyField(Term, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.title}'


class Challenge(CurlyQuotesMixin, models.Model):
    curly_fields = ['text']

    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return f'{self.title}'


class Solution(CurlyQuotesMixin, models.Model):
    curly_fields = ['text']

    challenge = models.OneToOneField(Challenge, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return f'{self.title}'


class Evaluation(CurlyQuotesMixin, models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='evaluations')

    def __str__(self):
        return f'Evaluation for lesson {self.lesson.title}'


class Question(CurlyQuotesMixin, models.Model):
    curly_fields = ['label']
    unwrap_p = True

    evaluation = models.ForeignKey(
        Evaluation, related_name='questions', on_delete=models.CASCADE)
    label = models.TextField()
    is_required = models.BooleanField(default=False)

    @property
    def has_multiple_answers(self):
        return self.answers.filter(is_correct=True).count() > 1

    @property
    def has_single_answer(self):
        return self.answers.filter(is_correct=True).count() == 1

    @property
    def has_answers(self):
        return self.has_single_answer or self.has_multiple_answers


class Answer(CurlyQuotesMixin, models.Model):
    curly_fields = ['label']

    question = models.ForeignKey(
        Question, related_name='answers', on_delete=models.CASCADE)
    label = models.TextField()
    is_correct = models.BooleanField(default=False)
