from django.core.exceptions import ValidationError
from django.db import models
from User.models import User
from Media.models import MediaFile
from cloudinary.models import CloudinaryField
from django.utils.timezone import now

class Event(models.Model):
    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("ongoing", "Ongoing"),
        ("previous", "previous"),
    ]

    title = models.CharField(max_length=255) 
    description = models.TextField()
    guidelines = models.TextField(blank=True, null=True)
    venue = models.CharField(max_length=255, blank=True, null=True)
    registration_start_date = models.DateTimeField(blank=True, null=True)
    registration_end_date = models.DateTimeField(blank=True, null=True)
    event_date = models.DateTimeField(blank=True, null=True)
    poster = CloudinaryField('poster', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="upcoming")
    gallery = models.ManyToManyField(MediaFile, related_name="event_gallery", blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    is_registrations_open = models.BooleanField(default=False)
    payment_required = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.status})"
    
    def clean(self):
        if self.registration_start_date and self.registration_end_date:
            if self.registration_start_date > self.registration_end_date:
                raise ValidationError("registration_start_date should be less than registration_end_date")
        
        if self.registration_end_date and self.event_date:
            if self.registration_end_date > self.event_date:
                raise ValidationError("registration_end_date should be less than event_date")
            
        if self.registration_start_date and self.event_date:
            if self.registration_start_date > self.event_date:
                raise ValidationError("registration_start_date should be less than event_date")
            
        if self.payment_required and not self.amount:
            raise ValidationError("Amount is required if payment is required")
        
        if self.amount and not self.payment_required:
            raise ValidationError("Payment is required if amount is provided")
        
        if self.amount and self.amount < 0:
            raise ValidationError("Amount should be greater than 0")
        
        
        super().clean()

    def save(self, *args, **kwargs):
        now_time = now()
        if self.event_date:
            if self.event_date > now_time:
                self.status = "upcoming"
            elif self.event_date <= now_time:
                self.status = "ongoing"

        self.full_clean()
        super().save(*args, **kwargs)






