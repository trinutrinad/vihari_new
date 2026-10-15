"""URL configuration for Bharat Yatra Django Admin."""

from __future__ import annotations

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("", admin.site.urls),
]

admin.site.site_header = "Bharat Yatra Admin"
admin.site.site_title = "Bharat Yatra Admin"
admin.site.index_title = "Platform catalog (shared DB)"
