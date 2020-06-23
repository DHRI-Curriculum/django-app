from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('workshop/', include('workshop.urls')),
    path('admin/', admin.site.urls),
    path('assessment/', include('assessment.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# handler404 = 'site.views.404'
