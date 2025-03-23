# Register your models here.

""" 
Now that we've created all our models, let's register them with Django's admin interface. This will allow us to easily view, create, and modify records during development.
"""

from django.contrib import admin
from .models import UserProfile
from .notification_models import Notification

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title')
    search_fields = ('user__username', 'user__email', 'job_title')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_preview', 'read', 'created_date')
    list_filter = ('read', 'created_date')
    search_fields = ('user__username', 'content')
    
    def content_preview(self, obj):
        """Return a truncated version of the content for the list display"""
        max_length = 50
        if len(obj.content) > max_length:
            return obj.content[:max_length] + '...'
        return obj.content
    
    content_preview.short_description = 'Content' # type: ignore