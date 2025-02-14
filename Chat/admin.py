from django.contrib import admin
from .models import Room, Message

# Inline for displaying messages in the Room admin
class MessageInline(admin.TabularInline):
    model = Message
    fields = ('sender', 'message_type', 'content_preview', 'created_at', 'is_deleted')
    readonly_fields = ('content_preview', 'created_at')
    extra = 0  # Removes the ability to add new messages directly in the inline form

    def content_preview(self, obj):
        """Short preview of the message content."""
        return obj.content[:50] if obj.content else "No content"
    
    content_preview.short_description = 'Content Preview'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'total_members', 'is_active', 'created_at', 'updated_at', 'created_by')
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'total_members', 'created_by')
    ordering = ('-created_at',)

    def total_members(self, obj):
        """Display the total number of members in the room."""
        return obj.members.count()
    
    total_members.short_description = 'Total Members'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'message_type', 'content_preview', 'created_at', 'is_deleted', 'is_edited')
    list_filter = ('room__name', 'message_type', 'is_deleted', 'created_at')
    search_fields = ('content', 'sender__username', 'room__name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    def content_preview(self, obj):
        """Short preview of the message content."""
        return obj.content[:50] if obj.content else "No content"

    content_preview.short_description = 'Content Preview'
