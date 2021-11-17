from django.urls import path

from .views import *

app_name = 'install'

urlpatterns = [
    path('', SoftwareIndexView.as_view(), name='index'),
    path('<str:slug>/', SoftwareView.as_view(), name='software'),
    path('<str:software_slug>/<str:os_slug>/', OSView.as_view(), name='instructions')
]
