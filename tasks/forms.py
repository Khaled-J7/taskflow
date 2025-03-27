# tasks/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Task, Comment, Attachment
from projects.models import Project

class TaskForm(forms.ModelForm):
    """Form for creating and updating tasks."""
    
    class Meta:
        model = Task
        
        # lists which model fields to include in the form
        fields = ['title', 'description', 'status', 'priority', 'due_date', 'assigned_to', 'tags']
        
        # customizes how specific fields are rendered in HTML
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        """
        Customize form initialization.
        If project_id is provided, filter available users to project members.
        """
        # Extract project_id from kwargs before calling parent __init__
        project_id = kwargs.pop('project_id', None)
        super().__init__(*args, **kwargs)
        
        # If project_id is provided, filter users to only project members
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                self.fields['assigned_to'].queryset = project.members.all() # type: ignore
            except Project.DoesNotExist:
                pass  # If project doesn't exist, keep the default queryset


class CommentForm(forms.ModelForm):
    """Form for creating and updating task comments."""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add your comment here...'}),
        }


class AttachmentForm(forms.ModelForm):
    """Form for uploading file attachments to tasks."""
    
    class Meta:
        model = Attachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }