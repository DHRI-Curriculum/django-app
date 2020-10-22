from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views
from . import views

app_name = 'glossary'

urlpatterns = [
  path('', views.Index.as_view(), name='index'),
  path('<str:slug>/', views.TermNav.as_view(), name='letter'),
  path('term/<str:slug>/', views.TermDetail.as_view(), name='term'),
]