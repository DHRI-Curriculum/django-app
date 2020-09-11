from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from .views import index, Feedback

app_name = 'feedback'

urlpatterns = [
  path('', index, name='index'),
  path('popup/<str:feedback_type>/', Feedback.as_view(), name='feedback_popup'),
  path('popup/<str:feedback_type>/<int:pk>/', Feedback.as_view(), name='feedback_popup')
]