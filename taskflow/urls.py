"""
URL configuration for taskflow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from os import name
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import home, register


""" 
The project-level urls.py file serves as the entry point for all URL routing in your Django project. It's like the main reception desk of a large office building that directs visitors to the right department.
When Django receives a request, it first looks at this main urls.py file to determine which app should handle the request. This file has several important responsibilities:

1. Central routing: It directs requests to the appropriate app based on URL patterns.
2. Project-wide URLs: It defines URLs that aren't specific to any particular app, like the home page or admin site.
3. URL namespacing: It organizes URLs into logical groups by assigning namespaces to included app URLs.
4. Media/static file serving: In development, it configures serving of media and static files.
"""

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
]

# Add this conditional for serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    """ 
    The added lines tell Django to serve files from the MEDIA_ROOT directory at URLs starting with MEDIA_URL, but only when DEBUG is True (i.e., during development). In production, you would configure your web server (Nginx, Apache, etc.) to serve these files instead.
    """
