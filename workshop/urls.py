from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import FrontmatterView, PraxisView, LessonView

app_name = 'workshop'

urlpatterns = [
  path('<str:slug>/', FrontmatterView.as_view(), name='frontmatter'),
  path('<str:slug>/theory-to-practice/', PraxisView.as_view(), name='praxis'),
  path('<str:slug>/lessons/', LessonView.as_view(), name='lesson'),
]