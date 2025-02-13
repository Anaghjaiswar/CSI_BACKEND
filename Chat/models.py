from django.db import models
from cloudinary.models import CloudinaryField
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Room(models.Model):
    ROOM_NAME_CHOICES = {
        "domain_based": [
            ("backend_2_3", "Backend (2+3)"),
            ("frontend_2_3", "Frontend (2+3)"),
            ("ml_2_3", "Machine Learning (2+3)"),
            ("designers_2_3", "Designers (2+3)"),
            ("app_dev_2_3", "App Development (2+3)"),
        ],
        "year_based": [
            ("2nd_year", "2nd Year"),
            ("3rd_year", "3rd Year"),
            ("4th_year", "4th Year"),
        ],
        "general_chat": [
            ("CSI_2_3", "CSI (2+3)"),
            ("CSI_2_3_4", "CSI (2+3+4)"),
        ],
    }

    name = models.CharField(max_length=50, choices=ROOM_NAME_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="rooms"
    )
    room_avatar = CloudinaryField("room_avatar", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

class Message(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ("text", "Text"),
        ("image", "Image"),
        ("file", "File"),
        ("reaction", "Reaction"),
    ]

    id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages"
    )
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField(blank=True, null=True)  # For text messages
    attachment = CloudinaryField("attachment", blank=True, null=True)  # For files/images
    parent_message = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", blank=True, null=True
    )  # For threaded messages
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="mentioned_in", blank=True
    ) # User mentions
    reactions = models.JSONField(blank=True, null=True)  # To store reactions as a JSON object
    is_deleted = models.BooleanField(default=False)  # Soft delete flag
    is_edited = models.BooleanField(default=False)  # Flag for edited messages
    status = models.JSONField(
        default=dict
    )  # To track message status like {"read_by": [user_ids], "delivered": True}
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message from {self.sender} in {self.room}"

    def delete_message(self):
        """Soft delete the message."""
        self.is_deleted = True
        self.save()

    def edit_message(self, new_content):
        """Edit the content of the message."""
        self.content = new_content
        self.is_edited = True
        self.save()
