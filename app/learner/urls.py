from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'learner'

urlpatterns = [
  path('', views.profile),
  path('profile/<str:username>/', views.profile, name='profile'),
]