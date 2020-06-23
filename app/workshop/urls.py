from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'workshop'

urlpatterns = [
  path('', views.index, name='index'),
  path('<str:slug>/', views.frontmatter, name='frontmatter'),
  path('<str:slug>/theory-to-practice/', views.praxis, name='praxis'),
  path('<str:slug>/lessons/<str:lesson_slug>', views.lesson, name='lesson'),
]