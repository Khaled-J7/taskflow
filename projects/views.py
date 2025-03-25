# projects/views.py

from enum import member
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db import transaction
from .models import Project, ProjectMember
from .forms import ProjectForm, ProjectMemberForm


""" 
📌 Django ORM Query Pattern Summary:

- Syntax : `Model.objects.method(field_name=value)`

- `field_name=value` is the condition for what records to retrieve (you can have multiple conditions)
"""

@login_required
def project_list(request):
    """
    Display a list of projects the user is a member of.
    The `@login_required` decorator ensures only logged-in users can access this view.
    """
    # Get all projects where the current user is a member
    projects = Project.objects.filter(members=request.user)

    return render(
        request,
        'projects/project_list.html',
        {'projects': projects}
    )


@login_required
def project_detail(request, pk):
    """
    Display detailed information about a specific project.
    This includes project details, tasks, and team members.
    """
    # Get the project or return 404 if not found
    project = get_object_or_404(Project, pk=pk)
    """
    `pk=pk` means "find a Project whose primary key equals the pk value we received from the URL
    """
    
    # Check if a user is a member of this project
    """ `request.user` refers to the user who is currently making the request to your web application."""
    if request.user not in project.members.all():
        return HttpResponseForbidden('You do not have access to this project.')
    
    # Get the user role in this project
    user_role = ProjectMember.objects.get(user=request.user, project=project).role
    
    # Get all tasks for this project (using the related_name we set in the `Task` model)
    # `project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')`
    tasks = project.tasks.all() # type: ignore
    
    # Get all members of this project
    members = ProjectMember.objects.filter(project=project)

    return render(
        request,
        'projects/project_detail.html',
        {
        'project': project,
        'tasks': tasks,
        'members': members,
        'user_role': user_role,
        }
    )
    
    
@login_required
def project_create(request):
    """
    Handle the creation of a new project.
    When a project is created, the creator is automatically
    added as a member with the 'admin' role.
    """
    if request.method == 'POST':
        form = ProjectForm(data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                """
                Ensures both operations succeed or fail together
                Uses transaction.atomic() to ensure that both the project creation and adding the creator as a member happen together (database integrity).
                """
                # Save the project
                project = form.save()
                
                # Add the creator as a member with 'admin' role
                ProjectMember.objects.create(
                    user=request.user,
                    project=project,
                    role='admin'
                )
                
                messages.success(request, f'Project "{project.title}" was created successfully!')
                
                return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
        
    return render(request, 'projects/project_form.html', {
        'form': form,
        'title': 'Create Project',
        'button_text': 'Create Project',
    })


@login_required
def project_update(request, pk):
    """
    Handle the update of an existing project.
    Only project admins should be able to update a project.
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user is an admin for this project
    try:
        membership = ProjectMember.objects.get(user=request.user, project=project)
        if membership.role != 'admin':
            return HttpResponseForbidden("Only project admins can edit project details.")
    except ProjectMember.DoesNotExist:
        return HttpResponseForbidden("You do not have access to this project.")
    
    if request.method == 'POST':
        """ 
        This below line creates a form instance pre-populated with both the submitted form data and an existing database object.
        - `request.POST`: is the first argument to the ProjectForm constructor and contains all the form data that was submitted by the user in the HTTP POST request.
        - The `instance `parameter is what makes this form operate in "update mode" rather than "create mode"
        - Without the `instance` parameter, calling form.save() would create a new record in the database, even if the form fields contained identical data to an existing record.
        """
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.title}" was updated successfully!')
            # Generates a complete URL like /projects/5/ (if the project's pk is 5)
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
        
    return render(
        request,
        'projects/project_form.html',
        {
         'form': form,
         'project': project,
         'title': 'Update Project',
         'button_text': 'Update Project',
        }
        )
        
#🚨 : Go for the `project_delete` implementation in claude AI and review what you did earlier