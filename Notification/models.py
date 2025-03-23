from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
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

class DeviceToken(models.Model):
    ANDROID = 'android'
    IOS = 'ios'
    DEVICE_TYPE_CHOICES = [
        (ANDROID, 'Android'),
        (IOS, 'iOS'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='device_tokens')
    device_token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPE_CHOICES, default=ANDROID)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} - {self.device_type} - {self.device_token[:10]}..."