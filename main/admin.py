from django.contrib import admin
from django.urls import path
from .models import SiteStatus
from . import views

class SiteStatusAdmin(admin.ModelAdmin):
    list_display = ['status']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('lock/', self.admin_site.admin_view(views.lock_site), name='lock_site'),
            path('unlock/', self.admin_site.admin_view(views.unlock_site), name='unlock_site'),
        ]
        return custom_urls + urls

admin.site.register(SiteStatus, SiteStatusAdmin)
