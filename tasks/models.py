from django.db import models
from django.contrib.auth.models import User
from projects.models import Project

# Create your models here.


class Tag(models.Model):
    """ 
    - Model for categorizing tasks with reusable labels.
    - Tags can be applied to multiple tasks, and tasks can have multiple tags.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    - Central model representing a work item within a project.
    - Tasks can be assigned to users, categorized with tags, and have comments and attachments.
    """
    # Basic task information
    title = models.CharField(max_length=100)
    description = models.TextField()

    # Project relationship - each task belongs to exactly one project
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='tasks')
    """ 
    The `related_name='tasks'` parameter is new here and very important. It customizes how we can access tasks from a project. Instead of the default project.task_set.all(), we can now use the more intuitive project.tasks.all(). This makes our code more readable
    """

    # Assignment relationship - a task can be assigned to one user (or none)
    assigned_to = models.ForeignKey(
        User,
        # If the assigned user is deleted, the task's assigned_to field becomes NULL rather than deleting the task. This preserves task history
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        # Allows accessing a user's assigned tasks with `user.assigned_tasks.all()`
        related_name='assigned_tasks'
    )

    # Task status with predefined choices
    status = models.CharField(max_length=20, choices=[
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done')
    ], default='todo')
    """ 
    Create dropdown options in forms.
    Each choice is a tuple of (stored_value, display_value):
    - The `stored_value` is what goes in the database
    - The `display_value` is what users see in forms and admin interfaces
    - The `default` parameter sets the initial value when a task is created
    """

    # Task priority with predefined choices
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium')

    # Date fields
    due_date = models.DateField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # Creator relationship - track who created the task
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )

    # Tags relationship - a task can have multiple tags
    tags = models.ManyToManyField(
        Tag,
        blank=True  # The blank=True means a task doesn't need to have any tags
    )

    def __str__(self):
        return self.title

    def is_overdue(self):
        """
        Check if the task is past its due date,
        It's not a field in the database but a computed property.
        This kind of method adds business logic to our model, making it more useful in our application.
        """
        from datetime import date
        if self.due_date and date.today() > self.due_date:
            return True
        return False


class Comment(models.Model):
    """
    Model for storing user comments on tasks.
    Each comment is connected to a specific task and has an author.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE,
                             related_name='comments')

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='task_comments')

    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.username} on '{self.task.title}'"


class Attachment(models.Model):
    """
    Model for storing files attached to tasks.
    Tracks file metadata and the user who uploaded the file.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE,
                             related_name='attachments')

    file = models.FileField(upload_to='attachments/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.IntegerField()   # Size in bytes
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='task_attachments')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name

    def save(self, *args, **kwargs):
        """
        - Override the save method to automatically fill file metadata
        - Django Provides a Python object (accessible as self.file) with helpful properties like:
            - `name`: The filename
            - `size`: The file size in bytes
            - `url`: The URL to access the file
            - Methods to read and manipulate the file
        However, Django doesn't automatically extract and store metadata about the file in separate fields. That's where our custom save method comes in.
        """
        # If this is a new attachment (no id yet) and we have a file
        if not self.id and self.file:  # type: ignore
            # Set the filename from the uploaded file
            self.file_name = self.file.name

            # Try to determine file type from extension
            name_parts = self.file.name.split('.')
            if len(name_parts) > 1:
                # takes the last part as the file type
                self.file_type = name_parts[-1].lower()
            else:
                self.file_type = 'unknown'

            # Set file size from the uploaded file
            self.file_size = self.file.size

        # Then we call the parent class's save method to do the actual saving
        super().save(*args, **kwargs)
