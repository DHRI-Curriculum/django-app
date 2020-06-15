from django.urls import path

from . import views

app_name = 'workshop'

urlpatterns = [
  path('', views.index, name='index'),
  path('<str:slug>/', views.index, name='index'),
]