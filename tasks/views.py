# tasks/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from projects.models import Project, ProjectMember
from .models import Task, Comment, Attachment
from .forms import CommentForm, TaskForm, AttachmentForm
from django.db.models import Q
from django.http import FileResponse
import os

@login_required
def task_create(request, project_id):
    """
    Handle the creation of a new task within a specific project.
    
    Args:
        request: The HTTP request
        project_id: ID of the project in which to create the task
    """
    # Get the project or return 404 if it doesn't exist
    project = get_object_or_404(Project, pk=project_id)
    
    # Check if user is a member of this project
    if request.user not in project.members.all():
        return HttpResponseForbidden("You do not have access to this project.")
    
    if request.method == 'POST':
        # Process the form submission
        form = TaskForm(request.POST, project_id=project_id)
        
        if form.is_valid():
            # Create a new task instance but don't save to database yet
            task = form.save(commit=False)
            
            # Set the project and creator
            task.project = project
            task.created_by = request.user
            
            # If no one is assigned, assign to the creator
            if not task.assigned_to:
                task.assigned_to = request.user
            
            # Save the task to the database
            task.save()
            
            # For many-to-many fields like tags, we need to call save_m2m()
            # after saving the instance when using commit=False
            form.save_m2m()
            
            messages.success(request, f'Task "{task.title}" was created successfully!')
            return redirect('projects:project_detail', pk=project.id) # type: ignore
    else:
        # Display the empty form for GET requests
        form = TaskForm(project_id=project_id)
        # Set the current user as the default assignee
        form.fields['assigned_to'].initial = request.user
    
    return render(request, 'tasks/task_form.html', {
        'form': form,
        'project': project,
        'title': 'Create Task',
        'button_text': 'Create Task',
    })
    
    
@login_required 
def task_detail(request, task_id):
    """
    Display detailed information about a specific task.
    
    Args:
        request: The HTTP request
        task_id: ID of the task to display
    """
    # 📌 Task Retrieval
    
    # Get the task or return 404 if it doesn't exist
    task = get_object_or_404(Task, pk=task_id)
    # Get the project that this task belongs to
    project = task.project
    
    # Check if user is a member of the project this task belongs to
    if request.user not in project.members.all():
        return HttpResponseForbidden("You do not have access to this task.")
    
    # Get the user's role in this project
    user_role = ProjectMember.objects.get(user=request.user, project=project).role
    
    # Get comments and attachments for this task
    comments = task.comments.all().order_by('created_date').reverse() # type: ignore
    attachments = task.attachments.all().order_by('upload_date').reverse() # type: ignore
    
    # Get other tasks in the same project for navigation
    # This will get the previous and next tasks based on ID
    previous_task = Task.objects.filter(project=project, id__lt=task.id).order_by('-id').first() # type: ignore # means "ID less than this task's ID" (previous task)
    next_task = Task.objects.filter(project=project, id__gt=task.id).order_by('id').first() # type: ignore
    # means "ID greater than this task's ID" (next task)
    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'project': project,
        'user_role': user_role,
        'comments': comments,
        'attachments': attachments,
        'previous_task': previous_task,
        'next_task': next_task,
    })



@login_required
def task_update(request, task_id):
    """
    Handle updating an existing task.
    
    Args:
        request: The HTTP request
        task_id: ID of the task to update
    """
    # 📌 Task Retrieval
    
    # Get the task or return 404 if it doesn't exist
    task = get_object_or_404(Task, pk=task_id)
    # Get the project that this task belongs to
    project = task.project
    
    # Check if user is a member of the project this task belongs to
    if request.user not in project.members.all():
        return HttpResponseForbidden("You do not have access to this task.")
    
    # Get the user's role to determine if they have edit permissions
    try:
        membership = ProjectMember.objects.get(user=request.user, project=project)
        
        # Only project admins, managers, task creator, or assigned user can edit
        if (membership.role not in ['admin', 'manager'] and # not project admins, managers
        request.user != task.created_by and     # not task creator
        request.user != task.assigned_to):      # not assigned user
            return HttpResponseForbidden("You do not have permission to edit this task.")
        
    except ProjectMember.DoesNotExist:
        return HttpResponseForbidden("You do not have access to this project.")
    
    # Form Processing
    if request.method == 'POST':
        # Process the form submission
        form = TaskForm(request.POST, instance=task, project_id=project.id) # type: ignore
        
        if form.is_valid():
            # Save the updated task
            form.save()
            
            messages.success(request, f'Task "{task.title}" was updated successfully!')
            return redirect('tasks:task_detail', task_id=task.id) # type: ignore
    else:
        # Display the form with the current task data
        form = TaskForm(instance=task, project_id=project.id) # type: ignore
    
    return render(request, 'tasks/task_form.html', {
        'form': form,
        'project': project,
        'task': task,
        'title': 'Update Task',
        'button_text': 'Save Changes',
    })
    
    
@login_required
def task_delete(request, task_id):
    """
    Handle the deletion of a task.
    
    Args:
        request: The HTTP request
        task_id: ID of the task to delete
    """
    # 📌 Task Retrieval
    
    # Get the task or return 404 if it doesn't exist
    task = get_object_or_404(Task, pk=task_id)
    project = task.project
    
    # 📌 Permission Check
    
    # Check if user is a member of the project this task belongs to
    if request.user not in project.members.all():
        return HttpResponseForbidden("You do not have access to this task.")
    
    # Get the user's role to determine if they have delete permissions
    try:
        membership = ProjectMember.objects.get(user=request.user, project=project)
        # Only project admins, managers or task creator can delete
        if membership.role not in ['admin', 'manager'] and request.user != task.created_by:
            return HttpResponseForbidden("You do not have permission to delete this task.")
    except ProjectMember.DoesNotExist:
        return HttpResponseForbidden("You do not have access to this project.")
    
    # 📌 Deletion Process
    if request.method == 'POST':
        # Store these values before deletion for use in the success message
        task_title = task.title
        project_id = project.id # type: ignore
        
        # Delete the task
        task.delete()
        
        messages.success(request, f'Task "{task_title}" was deleted successfully!')
        return redirect('projects:project_detail', pk=project_id)
    
    return render(request, 'tasks/task_confirm_delete.html', {
        'task': task,
        'project': project,
    })



@login_required
def add_comment(request, task_id):
    """
    Handle adding a new comment to a task.
    
    Args:
        request: The HTTP request
        task_id: ID of the task to comment on
    """
    # 📌 Task Retrieval
    
    # Get the task or return 404 if it doesn't exist
    task = get_object_or_404(Task, pk=task_id)
    project = task.project
    
    # 📌 Permission Check
    
    # Check if user is a member of the project this task belongs to
    if request.user not in project.members.all():
        return HttpResponseForbidden("You do not have access to this task.")
    
    # 📌 Comment Creation
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        
        if form.is_valid():
            # Create a new comment but don't save to database yet
            comment = form.save(commit=False)
            
            # Set the task and the author
            comment.task = task
            comment.author = request.user
            
            # Save the comment to the database
            comment.save()
            
            messages.success(request, 'Your comment was added successfully!')
            # redirects back to the task detail page after successful comment creation
            return redirect('tasks:task_detail', task_id=task.id) # type: ignore
        
    else:
        form = CommentForm()
        
    return render(request, 'tasks/add_comment.html', {
        'form': form,
        'task': task,
        'project': project,
    })



@login_required
def add_attachment(request, task_id):
    """
    Handle adding a file attachment to a task.
    
    Args:
        request: The HTTP request
        task_id: ID of the task to attach the file to
    """
    # 📌 Task Retrieval
    
    # Get the task or return 404 if it doesn't exist
    task = get_object_or_404(Task, pk=task_id)
    project = task.project
    
    # 📌 Permisson Check
    
    # Check if user is a member of the project this task belongs to
    if request.user not in project.members.all():
        return HttpResponseForbidden("You do not have access to this task.")
    
    # 📌 Attachment Process
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Create a new attachment but don't save to database yet
            attachment = form.save(commit=False)
            
            # Set the task and uploader
            attachment.task = task
            attachment.uploaded_by = request.user
            
            # The rest of the fields (file_name, file_type, file_size)
            # will be set automatically in the model's save method
            
            # Save the attachment to the database
            attachment.save()
            
            messages.success(request, 'Your file was uploaded successfully!')
            return redirect('tasks:task_detail', task_id=task.id) # type: ignore
    
    else:
        form = AttachmentForm()
        
    return render(request, 'tasks/add_attachment.html', {
        'form': form,
        'task': task,
        'project': project,
    })


@login_required
def download_attachment(request, attachment_id):
    """
    Handle downloading a file attachment.
    
    Args:
        request: The HTTP request
        attachment_id: ID of the attachment to download
    """
    # Get the attachment or return 404 if it doesn't exist
    attachment = get_object_or_404(Attachment, pk=attachment_id)
    task = attachment.task
    project = task.project
    
    # Check if user is a member of the project this task belongs to
    if request.user not in project.members.all():
        return HttpResponseForbidden("You do not have access to this file.")
    
    # Open the file and return it as a response
    file_path = attachment.file.path
    
    # Check if file exists
    if not os.path.exists(file_path):
        messages.error(request, f"File not found: {attachment.file_name}")
        return redirect('tasks:task_detail', task_id=task.id) # type: ignore
    
    # Return the file as a response
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{attachment.file_name}"'
    
    return response