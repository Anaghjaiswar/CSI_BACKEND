from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StudentProfile 

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'student':
        StudentProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_student_profile(sender, instance, **kwargs):
    if instance.role == 'student' and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
