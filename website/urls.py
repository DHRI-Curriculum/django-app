from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'website'

urlpatterns = [
  path('', views.index, name='index'),
  path('<str:page_slug>/', views.page, name='page'),
]