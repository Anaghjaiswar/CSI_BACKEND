from django.db import models
from User.models import User
from django.core.exceptions import ValidationError

class Announcement(models.Model):
    RELATED_CHOICES = (
        ('D', 'Domain Based'),
        ('T', 'Task'),
        ('M', 'Manual Selection'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annoucement_sender')
    receivers = models.ManyToManyField(User, related_name='announcement_receivers')
    message = models.TextField(help_text='announcement_content')
    related_to = models.CharField(max_length=1, choices=RELATED_CHOICES)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def clean(self):
        if self.sender and self.sender.role != 'admin':
            raise ValidationError('only users with admin role can send announcement')
        

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        


