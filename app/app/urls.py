from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('library/', include('library.urls')),
    path('workshops/', include('workshop.urls')),
    path('assessment/', include('assessment.urls')),
    path('', include('website.urls')),
]

urlpatterns += staticfiles_urlpatterns()

# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# handler404 = 'site.views.404'
