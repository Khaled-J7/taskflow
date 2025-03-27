# tasks/urls.py
from django.urls import path
from . import views

app_name = 'tasks'  # This creates a namespace for task URLs

urlpatterns = [
    path('project/<int:project_id>/create/',
         views.task_create, name='task_create'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('<int:task_id>/edit/', views.task_update, name='task_update'),
    path('<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('<int:task_id>/comment/add/', views.add_comment, name='add_comment'),
    path('<int:task_id>/attachment/add/',
         views.add_attachment, name='add_attachment'),
    path('attachment/<int:attachment_id>/download/',
         views.download_attachment, name='download_attachment'),
]
