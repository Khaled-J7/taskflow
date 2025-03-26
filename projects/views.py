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
    user_role = ProjectMember.objects.get(
        user=request.user, project=project).role

    # Get all tasks for this project (using the related_name we set in the `Task` model)
    # `project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')`
    tasks = project.tasks.all()  # type: ignore

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

                messages.success(
                    request, f'Project "{project.title}" was created successfully!')

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
        membership = ProjectMember.objects.get(
            user=request.user, project=project)
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
            messages.success(
                request, f'Project "{project.title}" was updated successfully!')
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


@login_required
def project_delete(request, pk):
    """
    Handle the deletion of a project.
    Only project admins should be able to delete a project.
    Deletion requires confirmation.
    """
    project = get_object_or_404(Project, pk=pk)

    # Check if user is an admin for this project
    try:
        membership = ProjectMember.objects.get(
            user=request.user, project=project)
        if membership.role != 'admin':
            return HttpResponseForbidden("Only project admins can delete projects.")
    except ProjectMember.DoesNotExist:
        return HttpResponseForbidden("You do not have access to this project.")

    if request.method == 'POST':
        # If confirmation received, delete the project
        project_title = project.title
        project.delete()
        messages.success(
            request, f'Project "{project_title}" was deleted successfully!')
        return redirect('projects:project_list')

    return render(request, 'projects/project_confirm_delete.html', {
        'project': project,
    })


@login_required
def manage_members(request, pk):
    """
    Handle adding, updating, and removing project members.
    Only project admins should be able to manage members.
    """
    project = get_object_or_404(Project, pk=pk)

    # Check if user is an admin for this project
    try:
        membership = ProjectMember.objects.get(
            user=request.user, project=project)
        if membership.role != 'admin':
            return HttpResponseForbidden("Only project admins can manage members.")
    except ProjectMember.DoesNotExist:
        return HttpResponseForbidden("You do not have access to this project.")

    # Get all current members
    members = ProjectMember.objects.filter(project=project)

    # Handle adding a new member
    if request.method == 'POST':
        form = ProjectMemberForm(request.POST, project=project)
        if form.is_valid():
            # Create a new ProjectMember but don't save yet
            member = form.save(commit=False)
            member.project = project  # Set the project
            member.save()

            messages.success(
                request, f'{member.user.username} was added to the project with role: {member.get_role_display()}')
            return redirect('projects:manage_members', pk=project.pk)
    else:
        form = ProjectMemberForm(project=project)

    return render(request, 'projects/manage_members.html', {
        'project': project,
        'members': members,
        'form': form,
    })


@login_required
def remove_member(request, project_pk, user_pk):
    """
    Remove a member from a project.
    Only project admins should be able to remove members.
    """
    project = get_object_or_404(Project, pk=project_pk)

    # Check if user is an admin for this project
    try:
        membership = ProjectMember.objects.get(
            user=request.user, project=project)
        if membership.role != 'admin':
            return HttpResponseForbidden("Only project admins can remove members.")
    except ProjectMember.DoesNotExist:
        return HttpResponseForbidden("You do not have access to this project.")

    # Get the membership to remove
    member_to_remove = get_object_or_404(
        ProjectMember, project=project, user_id=user_pk)

    # Prevent removing the last admin
    if member_to_remove.role == 'admin':
        admin_count = ProjectMember.objects.filter(
            project=project, role='admin').count()
        if admin_count <= 1:
            messages.error(
                request, "Cannot remove the last admin from the project.")
            return redirect('projects:manage_members', pk=project.pk)

    # Prevent self-removal
    if member_to_remove.user == request.user:
        messages.error(request, "You cannot remove yourself from the project.")
        return redirect('projects:manage_members', pk=project.pk)

    if request.method == 'POST':
        username = member_to_remove.user.username
        member_to_remove.delete()
        messages.success(request, f'{username} was removed from the project.')
        return redirect('projects:manage_members', pk=project.pk)

    return render(request, 'projects/confirm_remove_member.html', {
        'project': project,
        'member': member_to_remove,
    })


@login_required
def update_member_role(request, project_pk, user_pk):
    """
    Update a member's role in a project.
    Only project admins should be able to update roles.
    """
    project = get_object_or_404(Project, pk=project_pk)
    
    # Check if user is an admin for this project
    try:
        membership = ProjectMember.objects.get(user=request.user, project=project)
        if membership.role != 'admin':
            return HttpResponseForbidden("Only project admins can update member roles.")
    except ProjectMember.DoesNotExist:
        return HttpResponseForbidden("You do not have access to this project.")
    
    # Get the membership to update
    member_to_update = get_object_or_404(ProjectMember, project=project, user_id=user_pk)
    
    # On POST requests, it updates the member's role and redirects to the manage members page.
    if request.method == 'POST':
        form = ProjectMemberForm(request.POST, instance=member_to_update)
        if form.is_valid():
            # Check that we're not removing the last admin
            if member_to_update.role == 'admin' and form.cleaned_data['role'] != 'admin':
                admin_count = ProjectMember.objects.filter(project=project, role='admin').count()
                if admin_count <= 1:
                    messages.error(request, "Cannot change the role of the last admin.")
                    return redirect('projects:manage_members', pk=project.pk)
            
            form.save()
            messages.success(request, f"Updated {member_to_update.user.username}'s role to {member_to_update.get_role_display()}") # type: ignore
            return redirect('projects:manage_members', pk=project.pk)
    else:
        form = ProjectMemberForm(instance=member_to_update)
    
    return render(request, 'projects/update_member_role.html', {
        'form': form,
        'project': project,
        'member': member_to_update,
    })

