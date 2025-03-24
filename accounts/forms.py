# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm  # built-in form

class UserRegistrationForm(UserCreationForm):
    """Form for user registration, extends Django's UserCreationForm."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        """ 'password1', 'password2' --> password confirmation"""
        
    def clean_email(self):
        """
        Validate that the email is unique.
        The naming convention `clean_<fieldname>` is how Django knows to use this method for validating that specific field.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email