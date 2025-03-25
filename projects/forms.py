# projects/forms.py
from django import forms
from .models import Project, ProjectMember
from django.contrib.auth.models import User

class ProjectForm(forms.ModelForm):
    """Form for creating and updating projects."""
    
    class Meta:
        model = Project
        fields = ['title', 'description', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        """
        The `widgets` dictionary in Meta customizes how each field is rendered. Here, we're making the description field a larger textarea with 4 rows.
        """ 
        

class ProjectMemberForm(forms.ModelForm):
    """Form for adding and updating project members."""
    
    class Meta:
        model = ProjectMember
        fields = ['user', 'role']
        
    def __init__(self, *args, **kwargs):
        """
        The __init__ method in ProjectMemberForm is overridden to customize the user dropdown. If a project is provided, it filters out users who are already members of that project, preventing duplicates.
        """
        project = kwargs.pop('project', None)
        super.__init__(*args, **kwargs)
        
        if project:
            # Get all users who are already members of this project
            existing_members = project.members.all()
            # Filter out these users from the dropdown
            self.fields['user'].queryset = User.objects.exclude(id__in=[user.id for user in existing_members]) # type: ignore
