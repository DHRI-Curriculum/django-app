from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from . import views

app_name = 'feedback'

urlpatterns = [
  path('', views.index, name='index'),
  path('popup/lesson/<int:lesson_id>', views.lesson_popup, name='lesson_popup'),
  path('thank_you', views.thank_you, name='thank_you'),
]