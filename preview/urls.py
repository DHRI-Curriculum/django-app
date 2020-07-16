from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'preview'

urlpatterns = [
  path('', views.menu, name='menu'),
  path('<str:repo>/', views.repository, name='repository'),
  path('<str:repo>/frontmatter/', views.frontmatter, name='frontmatter'),
  path('<str:repo>/praxis/', views.praxis, name='praxis'),
  path('<str:repo>/lessons/', views.lessons, name='lessons'),
]