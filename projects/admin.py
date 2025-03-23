from django.contrib import admin
from .models import Project, ProjectMember

""" 
Now that we've created all our models, let's register them with Django's admin interface. This will allow us to easily view, create, and modify records during development.
"""

class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_date')
    list_filter = ('status', 'created_date')
    search_fields = ('title', 'description')
    inlines = [ProjectMemberInline]

@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'joined_date')
    list_filter = ('role', 'joined_date')
    search_fields = ('user__username', 'project__title')