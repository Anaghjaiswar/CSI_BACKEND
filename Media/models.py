from django.db import models
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
import mimetypes

class MediaFile(models.Model):
    file = CloudinaryField("media_file")  # Cloudinary file field
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)


    def __str__(self):
        return self.title
    
    def clean(self):
        if self.file_size and self.file_size > 10 * 1024 * 1024:
            raise ValidationError("File size must be less than 10MB.")
        super().clean()