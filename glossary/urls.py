from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .views import Index, TermDetail

app_name = 'glossary'

urlpatterns = [
  path('', Index.as_view(), name='index'),
  path('<str:slug>/', TermDetail.as_view(), name='term'),
]