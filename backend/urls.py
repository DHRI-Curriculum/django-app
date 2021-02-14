from django.urls import path
# from django.views.generic import RedirectView

from . import views

app_name = 'backend'

urlpatterns = [
  path('', views.IndexRedirect.as_view(), name='index'),
  path('term/<str:slug>/', views.TermRedirectView.as_view()),
  path('insight/<str:slug>/', views.InsightRedirectView.as_view()),
  path('install/<str:slug>/', views.InstallRedirectView.as_view()),
  path('workshop/<str:slug>/', views.WorkshopRedirectView.as_view()),
]