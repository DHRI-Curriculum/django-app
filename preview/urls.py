from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'preview'

urlpatterns = [
  path('', views.menu, name='menu'),
  path('<str:repository>/', views.repository, name='repository'),
  path('<str:repository>/frontmatter/', views.frontmatter, name='frontmatter'),
  path('<str:repository>/praxis/', views.praxis, name='praxis'),
  path('<str:repository>/lessons/', views.lessons, name='lessons'),
]