from django import forms

class TestForm(forms.Form):
    test_question = forms.CharField(label='Test question', max_length=100)
