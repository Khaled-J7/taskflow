from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    """
    Model for storing system notifications for users.
    
    Notifications can be about various events like task assignments,
    comments, approaching deadlines, etc. and include a link to the
    relevant resource.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                            related_name='notifications')
    
    content = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    read = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        ordering = ['-created_date']  # Show newest notifications first
        
    
    def __str__(self):
        """Return a string representation showing recipient and preview of content"""
        # Truncate content if it's too long for the string representation
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"Notification for {self.user.username}: {preview}"
    
    
    def mark_as_read(self):
        """Mark this notification as read and save the change"""
        self.read = True
        self.save(update_fields=['read'])
        
    
    @classmethod
    def create_notification(cls, user, content, link=''):
        """
        Class method to create a notification more easily.
        `Class methods (defined with @classmethod) are methods that are bound to the class rather than an instance, and they receive the class itself as their first parameter (conventionally named cls instead of self).`
        Example:
            Notification.create_notification(
                user=request.user,
                content="You have been assigned a new task",
                link="/tasks/42/"
            )
        """
        notification = cls(user=user, content=content, link=link)
        notification.save()
        return notification