from django.urls import path
from . import views

app_name = 'assessment'

urlpatterns = [
    path('', views.index, name='index'),
    path('question/<int:question_id>/', views.Test.as_view(), name='test'),
]
