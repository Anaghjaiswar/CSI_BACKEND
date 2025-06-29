from django.utils import timezone
from django.db import models
from cloudinary.models import CloudinaryField
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Room(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="rooms"
    )
    room_avatar = CloudinaryField("room_avatar", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_rooms"
    )

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
    ) 
    reactions = models.JSONField(blank=True, null=True)  
    is_deleted = models.BooleanField(default=False) 
    is_edited = models.BooleanField(default=False)  
    status = models.JSONField(
        default=dict
    )
    is_pinned = models.BooleanField(default=False)
    pinned_at = models.DateTimeField(null=True, blank=True)
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

    def pin(self):
        from django.core.exceptions import ValidationError
        # enforce max 3 pinned per room
        pinned_count = Message.objects.filter(room=self.room, is_pinned=True).count()
        if pinned_count >= 3 and not self.is_pinned:
            raise ValidationError("You can only pin up to 3 messages per room.")
        self.is_pinned = True
        self.pinned_at = timezone.now()
        self.save(update_fields=["is_pinned", "pinned_at"])

    def unpin(self):
        self.is_pinned = False
        self.pinned_at = None
        self.save(update_fields=["is_pinned", "pinned_at"])

    def save(self, *args, **kwargs):
        """
        Override the save method to ensure the sender is a member of the room.
        """
        if not self.room.members.filter(id=self.sender.id).exists():
            raise ValueError("The sender must be a member of the room to send a message.")
        super().save(*args, **kwargs)

class UserRoomStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="room_statuses")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="user_statuses")
    last_read = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'room')

    def __str__(self):
        return f"{self.user} in {self.room} last read at {self.last_read}"
