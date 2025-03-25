# projects/urls.py
from django.urls import path
from . import views

""" 
app_name = 'projects' sets up URL namespacing, allowing you to reference URLs as 'projects:project_list' in templates.
This creates a namespace for projects URLs
"""
app_name = 'projects'


urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('new/', views.project_create, name='project_create'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
#     path('<int:pk>/edit/', views.project_update, name='project_update'),
#     path('<int:pk>/delete/', views.project_delete, name='project_delete'),
#     path('<int:pk>/members/', views.manage_members, name='manage_members'),
#     path('<int:project_pk>/members/<int:user_pk>/remove/', views.remove_member, name='remove_member'),
#     path('<int:project_pk>/members/<int:user_pk>/update-role/', views.update_member_role, name='update_member_role'),
]