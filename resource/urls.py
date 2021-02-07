from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'resource'

urlpatterns = [
  path('', views.Index.as_view(), name='index'),
  path('load/', views.lazyload, name='lazyload'),
  path('load/<str:category>', views.lazyload, name='lazyload'),
  path('<str:category>', views.Category.as_view(), name='category'),
]