from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from learner import views as learner_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('library/', include('library.urls')),
    path('workshops/', include('workshop.urls')),
    path('assessment/', include('assessment.urls')),
    path('learner/', include('learner.urls')),
    path('sign-up/', learner_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='learner/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='learner/logout.html'), name='logout'),
    path('', include('website.urls')),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# handler404 = 'site.views.404'
