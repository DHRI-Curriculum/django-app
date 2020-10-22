from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'website'

urlpatterns = [
  path('', views.Index.as_view(), name='index'),
  path('<str:slug>/', views.PageView.as_view(), name='page'),
]