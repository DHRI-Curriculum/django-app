from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from learner import views as learner_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('library/', RedirectView.as_view(pattern_name='resource:index', permanent=False)),
    path('resource/', include('resource.urls')),
    path('workshops/', include('workshop.urls')),
    path('assessment/', include('assessment.urls')),
    path('learner/', include('learner.urls')),
    path('glossary/', include('glossary.urls')),
    path('feedback/', include('feedback.urls')),
    path('installations/', include('install.urls')),
    path('insights/', include('insight.urls')),
    path('shortcuts/', include('backend.urls')),
    path('register/', learner_views.Register.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='learner/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='learner/logout.html'), name='logout'),
    path('reset-password/', auth_views.PasswordResetView.as_view(template_name='learner/password_reset.html'), name='password_reset'),
    path('', include('website.urls')),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# handler404 = 'site.views.404'
