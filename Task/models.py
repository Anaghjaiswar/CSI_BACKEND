from django.db import models
from django.core.exceptions import ValidationError
from User.models import User
from cloudinary.models import CloudinaryField
from datetime import date


class Group(models.Model):
    """
    Represents a group of members assigned to a task.
    """
    name = models.CharField(max_length=255)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name="groups")
    members = models.ManyToManyField(User, related_name="group_members")

    def __str__(self):
        return f"{self.name} (Task: {self.task.title})"
    
    def clean(self):
        """
        Ensure unique group names per task.
        """
        if Group.objects.filter(name=self.name, task=self.task).exists():
            raise ValidationError(f"A group with the name '{self.name}' already exists for this task.")


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Task'),
        ('current', 'Current Task'),
        ('completed', 'Completed Task')
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks_assigned_by")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='current')  # Default value added
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_progress = models.IntegerField(default=0)
    attachment = CloudinaryField('file', blank=True, null=True)
    info_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

    def clean(self):
        """
        Add model-level validation for start_date, end_date, and task assignment rules.
        """
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be earlier than start date.")

        # Validate assigned_by rules
        if hasattr(self.assigned_by, 'year'):
            for group in self.groups.all():
                for user in group.members.all():
                    if self.assigned_by.year == '2nd':
                        raise ValidationError("2nd-year users cannot assign tasks to anyone.")
                    elif self.assigned_by.year == '3rd' and user.year != '2nd':
                        raise ValidationError("3rd-year users can only assign tasks to 2nd-year users.")
                    elif self.assigned_by.year == '4th' and user.year not in ['2nd', '3rd']:
                        raise ValidationError("4th-year users can only assign tasks to 2nd or 3rd-year users.")

        # Validate progress
        if not (0 <= self.current_progress <= 100):
            raise ValidationError("Current progress must be between 0 and 100.")

    def save(self, *args, **kwargs):
        """
        Override save method to ensure a default group is created.
        """
        super().save(*args, **kwargs)  # Save the task first to get an ID
        # if not self.groups.filter(name="Default Group").exists():
        #     default_group = Group.objects.create(name="Default Group", task=self)
        #     default_group.save()

    def get_status(self):
        """
        Dynamically determine the status of the task based on dates and completion status.
        """
        if self.current_progress == 100:
            return 'completed'
        if self.start_date <= date.today() <= self.end_date and self.status != 'completed':
            return 'current'
        if self.end_date < date.today() and self.status != 'completed':
            return 'pending'
        return self.status



