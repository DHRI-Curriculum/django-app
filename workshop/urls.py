from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views
from lesson.views import CheckAnswer

app_name = 'workshop'

urlpatterns = [
  path('', views.IndexRedirect.as_view(), name='index'),
  path('<str:slug>/', views.FrontmatterView.as_view(), name='frontmatter'),
  path('<str:slug>/theory-to-practice/', views.PraxisView.as_view(), name='praxis'),
  path('<str:slug>/lessons/', views.LessonView.as_view(), name='lesson'),
  path('<str:slug>/lessons/check-answer/', CheckAnswer.as_view()),
]