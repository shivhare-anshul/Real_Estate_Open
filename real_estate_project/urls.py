"""
URL configuration for real_estate_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('endpoints.urls')),
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
]
