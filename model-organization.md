# TaskFlow Model Organization

This document outlines the complete model structure for the TaskFlow project, organized by Django apps. It provides details on model fields, relationships, and their purposes.

## 1. Accounts App

The accounts app handles user-related functionality including authentication, profiles, and notifications.

### UserProfile Model

Extends Django's built-in User model with additional profile information.

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    notification_preferences = models.JSONField(default=dict, blank=True)
```

**Relationships:**
- One-to-One with User (Django's built-in user model)

**Purpose:** Stores additional user information beyond authentication details.

### Notification Model

Manages system notifications for users.

```python
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    read = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
```

**Relationships:**
- Many-to-One with User (a user can have many notifications)

**Purpose:** Provides a system for notifying users about events (task assignments, comments, etc.)

## 2. Projects App

The projects app manages project-related functionality and the relationship between users and projects.

### Project Model

Contains core project information.

```python
class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('archived', 'Archived')
    ], default='active')
    members = models.ManyToManyField(User, through='ProjectMember')
```

**Relationships:**
- Many-to-Many with User (through ProjectMember)
- One-to-Many with Task (a project can have many tasks)

**Purpose:** Organizes tasks into logical groupings (projects).

### ProjectMember Model

Junction table connecting Users to Projects with additional membership information.

```python
class ProjectMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Admin'),
        ('manager', 'Project Manager'),
        ('member', 'Team Member')
    ])
    joined_date = models.DateTimeField(auto_now_add=True)
```

**Relationships:**
- Many-to-One with User
- Many-to-One with Project

**Purpose:** Manages project membership and roles, implementing a many-to-many relationship between users and projects with additional data.

## 3. Tasks App

The tasks app manages task-related functionality, including tags, comments, and attachments.

### Task Model

Central model containing task information.

```python
class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                    null=True, blank=True, related_name='assigned_tasks')
    status = models.CharField(max_length=20, choices=[
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done')
    ], default='todo')
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium')
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, 
                                   related_name='created_tasks')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
```

**Relationships:**
- Many-to-One with Project
- Many-to-One with User (assigned_to)
- Many-to-One with User (created_by)
- Many-to-Many with Tag
- One-to-Many with Comment
- One-to-Many with Attachment

**Purpose:** Represents individual work items within projects.

### Tag Model

Simple model for task categorization.

```python
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
```

**Relationships:**
- Many-to-Many with Task

**Purpose:** Provides a tagging/categorization system for tasks.

### Comment Model

Stores user comments on tasks.

```python
class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
```

**Relationships:**
- Many-to-One with Task
- Many-to-One with User

**Purpose:** Allows users to comment on tasks for discussion and collaboration.

### Attachment Model

Manages files attached to tasks.

```python
class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.IntegerField()  # Size in bytes
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
```

**Relationships:**
- Many-to-One with Task
- Many-to-One with User

**Purpose:** Enables users to attach files to tasks.

## Database Relationship Diagram

```
User (1) ───────────── (1) UserProfile
  │
  │
  │ (M)
  ▼
ProjectMember
  │
  │ (M)
  ▼
Project (1) ─────────── (M) Task (M) ─────────── (M) Tag
                          │
                          │ (1)
                          ▼
                     Comment (M) ◄─── (1) User
                          │
                          │
                     Attachment (M) ◄─── (1) User
                          │
                          │
                     Notification (M) ◄─── (1) User
```

## Implementation Notes

1. **Django's User Model**: We're extending Django's built-in User model using a one-to-one relationship with UserProfile rather than creating a custom User model.

2. **Many-to-Many Relationships**: For the relationship between Task and Tag, we'll use Django's default many-to-many implementation which automatically creates the junction table. For User and Project, we use a custom through model (ProjectMember) to store additional data.

3. **Cascading Deletions**: The `on_delete=models.CASCADE` parameter means when a parent object is deleted, related objects will also be deleted. This is used in most relationships except for Task.assigned_to, where we use `SET_NULL` to avoid deleting tasks when users are removed.

4. **Auto-generated Fields**: We use `auto_now_add=True` for creation timestamps and `auto_now=True` for update timestamps, letting Django handle these automatically.

5. **Null vs. Blank**: 
   - `null=True`: Allows NULL values in the database
   - `blank=True`: Allows empty values in forms
   - For optional text fields, usually only `blank=True` is needed
   - For optional relationships and date fields, both are required
