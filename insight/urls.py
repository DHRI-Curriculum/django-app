from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import Index, InsightDetail

app_name = 'insight'

urlpatterns = [
  path('', Index.as_view(), name='index'),
  path('<str:slug>/', InsightDetail.as_view(), name='insight'),
]