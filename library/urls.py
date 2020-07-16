from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'library'

urlpatterns = [
  # path('', views.index, name='index'),
  path('project/<str:pk>/', views.project_details, name='project_details'),
  path('load-projects/', views.lazyload_projects, name='project_lazyloader'),
  path('load-readings/', views.lazyload_readings, name='reading_lazyloader'),
  path('load-tutorials/', views.lazyload_tutorials, name='tutorials_lazyloader'),
  path('load-resources/', views.lazyload_resources, name='resources_lazyloader'),
]