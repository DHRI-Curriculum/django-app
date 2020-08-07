from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from . import views

app_name = 'feedback'

urlpatterns = [
  path('', views.index, name='index'),
  path('popup/<str:feedback_type>/', views.feedback_popup, name='feedback_popup'),
  path('popup/<str:feedback_type>/<int:pk>/', views.feedback_popup, name='feedback_popup')
]