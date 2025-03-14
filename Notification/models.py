from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
# Create your models here.

User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    url = models.URLField(blank=True, null=True) 
    event_type = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification for {self.user} - {self.event_type} - {self.message}"

    def mark_as_read(self):
        """Mark the notification as read"""
        self.is_read = True
        self.save()

