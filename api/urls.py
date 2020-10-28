from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'api'

urlpatterns = [
  path('', views.Endpoints.as_view(), name='endpoints'),
  path('workshops/<str:slug>/', views.Workshops.as_view(), name='workshop'),
  path('workshops/', views.Workshops.as_view(), name='workshops'),
  path('terms/<str:slug>/', views.Terms.as_view(), name='term'),
  path('terms/', views.Terms.as_view(), name='terms'),
]