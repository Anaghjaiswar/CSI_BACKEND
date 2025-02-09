from django.db import models
from cloudinary.models import CloudinaryField


class Domain(models.Model):
    DOMAIN_CHOICES = [
        ('BACKEND', 'Backend'),
        ('FRONTEND', 'Frontend'),
        ('APP_DEV', 'App Development'),
        ('ML', 'Machine Learning'),
        ('UI/UX_DEV', 'UI/UX Development'),
        ('FULL_STACK','Full Stack Development')
    ]

    name = models.CharField(max_length=20, choices=DOMAIN_CHOICES, unique=True)
    description = models.TextField()
    image = CloudinaryField('image', blank=True, null=True, help_text="Upload an image representing this domain.")
    goals = models.TextField(blank=True, null=True, help_text="Goals of the domain.")

    def __str__(self):
        return dict(self.DOMAIN_CHOICES).get(self.name, "Unknown Domain")
