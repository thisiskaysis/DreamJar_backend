"""
URL configuration for dreamjar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users.views import CustomAuthToken
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from auth_kit.views import AuthKitUIView
from django.conf import settings

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('auth_kit.urls')),
    path('api/auth/social/', include('auth_kit.social.urls')),
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path("accounts/", include("allauth.urls")),
    path("_allauth/", include("allauth.headless.urls")),
    path('accounts/', include('allauth.urls')),
    path('', include('users.urls')),
    path('', include('campaigns.urls')),
    path('', include('donations.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('api/auth/ui/', AuthKitUIView.as_view(), name='auth_kit_ui')
    ]