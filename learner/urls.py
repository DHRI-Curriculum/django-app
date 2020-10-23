from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from . import views

app_name = 'learner'

urlpatterns = [
  path('', views.Detail.as_view()),
  path('favorite/', views.favorite, name='favorite'),
  path('instructor-request/', views.InstructorRequests.as_view(), name='instructor_request'),
  path('requests/', views.InstructorRequests.as_view(), name='instructor_requests'),
  path('profile/<str:username>/', views.Detail.as_view(), name='profile'),
  path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]