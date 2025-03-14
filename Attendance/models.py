from django.conf import settings
from django.db import models
from django.utils import timezone

class Attendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    
    # Check-In fields
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_in_latitude = models.FloatField()
    check_in_longitude = models.FloatField()
    check_in_within_range = models.BooleanField(default=False)
    
    # Check-Out fields
    check_out_time = models.DateTimeField(null=True, blank=True)
    check_out_latitude = models.FloatField(null=True, blank=True)
    check_out_longitude = models.FloatField(null=True, blank=True)
    check_out_within_range = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.first_name} - {self.date}"
