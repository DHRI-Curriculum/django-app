from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import Index, PageView

app_name = 'website'

urlpatterns = [
  path('', Index.as_view(), name='index'),
  path('<str:slug>/', PageView.as_view(), name='page'),
]