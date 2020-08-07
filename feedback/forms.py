from django import forms
from .models import Issue
from django.contrib.auth.models import User

class IssueForm(forms.ModelForm):
    comment = forms.CharField(required=True, widget=forms.Textarea)

    class Meta:
        model = Issue
        fields = ['comment']
