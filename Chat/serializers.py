from rest_framework import serializers
from .models import Room, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    # return cloudinary url of photo use_url=True
    photo = serializers.ImageField(use_url=True)
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "role", "photo", "year"]

class RoomSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(source="members.count", read_only=True)

    class Meta:
        model = Room
        fields = ["id", "name", "description", "room_avatar", "created_at", "updated_at", "members_count"]

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "sender", "message_type", "content", "attachment", "created_at", "updated_at"]
