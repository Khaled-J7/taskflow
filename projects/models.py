from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Project(models.Model):
    
    # A short name for the project (limited to 100 characters)
    title = models.CharField(max_length=100)
    
    # A detailed explanation of the project (unlimited text)
    description = models.TextField()
    
    # Automatically set to the current time when the project is created
    created_date = models.DateTimeField(auto_now_add=True)
    
    # Tracks whether the project is active or archived, with a default of 'active'
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('archived', 'Archived')
    ], default='active')
    """ 
    Create dropdown options in forms.
    Each choice is a tuple of (stored_value, display_value):
    - The `stored_value` is what goes in the database
    - The `display_value` is what users see in forms and admin interfaces
    - The `default` parameter sets the initial value when a task is created
    """
    
    # Many-to-Many Relationship with User Model
    members = models.ManyToManyField(User, through='ProjectMember')
    """
    - Each Project can have multiple User members
    - Each User can be a member of multiple Projects
    - The `through='ProjectMember'` parameter is crucial - it specifies a custom intermediary model for this relationship. Normally, Django would create a hidden junction table with just project_id and user_id columns. By specifying our own model, we can add extra data about the relationship (like roles and join dates)
    """
    
    def __str__(self):
        return self.title
    
    
class ProjectMember(models.Model):
    """ The ProjectMember model serves as the junction table between User and Project """
    
    # Each ProjectMember is linked to exactly one User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Each ProjectMember is linked to exactly one Project
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    # Defines what permissions/responsibilities the user has in this specific project
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Admin'),
        ('manager', 'Project Manager'),
        ('member', 'Team Member')
    ])
    
    # Automatically records when the user was added to the project
    joined_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """ 
        This creates a database constraint ensuring that a user can only be a member of a project once. It prevents duplicate memberships, which would cause confusion about which role applies.
        """
        unique_together = ('user', 'project')   # Ensures a user can only be added once to a project
        
    def __str__(self):
        return f"{self.user.username} - {self.project.title} ({self.role})"
    

         