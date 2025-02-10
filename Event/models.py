from django.core.exceptions import ValidationError
from django.db import models
from User.models import User
from Media.models import MediaFile
# from django.utils.timezone import now

class Event(models.Model):
    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("ongoing", "Ongoing"),
        ("previous", "previous"),
    ]

    title = models.CharField(max_length=255) 
    description = models.TextField()  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="upcoming")
    registration_date = models.DateTimeField(blank=True, null=True)  
    event_date = models.DateTimeField(blank=True, null=True) 
    location = models.CharField(max_length=500, blank=True, null=True)
    online_link = models.URLField(blank=True, null=True)
    organizers = models.ManyToManyField(User, related_name="organized_events", blank=True)  
    media_files = models.ManyToManyField(MediaFile, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    is_registrations_open = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.status})"
    
    def clean(self):
        if self.registration_date is None or self.event_date is None:
            # Skip validation if fields are not provided
            return 

        if self.event_date <= self.registration_date:
            raise ValidationError("Event date must be after the registration date.")

        super().clean()





