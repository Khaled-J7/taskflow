from django.contrib import admin
from .models import Task, Tag, Comment, Attachment

""" 
Now that we've created all our models, let's register them with Django's admin interface. This will allow us to easily view, create, and modify records during development.
"""

class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    fields = ('file', 'file_name', 'file_type', 'file_size', 'uploaded_by', 'upload_date')
    readonly_fields = ('file_name', 'file_type', 'file_size', 'upload_date')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'priority', 'due_date')
    list_filter = ('status', 'priority', 'due_date', 'project')
    search_fields = ('title', 'description', 'assigned_to__username')
    filter_horizontal = ('tags',)
    inlines = [CommentInline, AttachmentInline]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'content_preview', 'created_date')
    list_filter = ('created_date',)
    search_fields = ('content', 'author__username', 'task__title')
    
    def content_preview(self, obj):
        max_length = 50
        if len(obj.content) > max_length:
            return obj.content[:max_length] + '...'
        return obj.content
    
    content_preview.short_description = 'Content' # type: ignore

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'task', 'file_type', 'file_size_display', 'uploaded_by', 'upload_date')
    list_filter = ('file_type', 'upload_date')
    search_fields = ('file_name', 'task__title', 'uploaded_by__username')
    readonly_fields = ('file_size_display',)
    
    def file_size_display(self, obj):
        """Convert file size from bytes to a more readable format"""
        # Convert file size to KB, MB, etc.
        size_bytes = obj.file_size
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    file_size_display.short_description = 'File Size' # type: ignore