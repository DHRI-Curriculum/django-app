from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import Index, Detail

app_name = 'install'

urlpatterns = [
  path('', Index.as_view(), name='index'),
  path('<str:slug>/', Detail.as_view(), name='installation')
]