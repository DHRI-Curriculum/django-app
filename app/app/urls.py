from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('workshop/', include('workshop.urls')),
    path('admin/', admin.site.urls),
    path('assessment/', include('assessment.urls')),
]