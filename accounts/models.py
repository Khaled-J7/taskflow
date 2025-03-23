from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .notification_models import Notification

# Create your models here.
class UserProfile(models.Model):
    # One-to-One relationship with the built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Profile picture with a specific upload directory for better organization
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Text field for user biography (unlimited length)
    bio = models.TextField(blank=True)
    
    # Character field with maximum length for job title, `blank=True` makes it optional
    job_title = models.CharField(max_length=100, blank=True)
    
    # This field stores the user's notification preferences
    notification_preferences = models.JSONField(default=dict, blank=True)
    """
    - JSONField is a specialized field that stores data in JSON format
    - It allows storing complex, structured data without creating additional database tables
    - default=dict means it starts as an empty dictionary `({})` if no value is provided
    - blank=True makes it optional in forms
    """
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
# Signal to automatically create a UserProfile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ 
    This function is triggered after a User is saved (post_save). The created parameter is True when the User is being created for the first time. In that case, the function creates a new UserProfile for the User.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ 
    This function is also triggered after a User is saved. It ensures that whenever a User object is saved, the associated UserProfile is also saved.
    """
    instance.userprofile.save()
