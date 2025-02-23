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


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    attachment = serializers.ImageField(use_url=True)
    

    class Meta:
        model = Message
        fields = '__all__' 

class UserForRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name"]

class LastMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'content', 'created_at', 'sender']

    def get_sender(self, obj):
        return {
            "id": obj.sender.id,
            "first_name": obj.sender.first_name,
            "last_name": obj.sender.last_name,
        }



class RoomSerializer(serializers.ModelSerializer):
    room_avatar = serializers.ImageField(use_url=True, required=False)
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True
    )
    # members_detail = UserForRoomSerializer(many=True, read_only=True, source="members")
    created_by = UserForRoomSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'members', 'room_avatar', 'is_active', 'created_by', 'created_at', 'updated_at', 'last_message']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        room = Room.objects.create(**validated_data)
        room.members.set(members)  # Add members to the room
        return room
    
    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        return LastMessageSerializer(last_message).data if last_message else None


class EditRoomSerializer(serializers.ModelSerializer):
    room_avatar = serializers.ImageField(use_url=True, required=False)
    members = UserForRoomSerializer(read_only=True)  # Prevent editing of members

    class Meta:
        model = Room
        fields = [
            "name",
            "description",
            "members",
            "room_avatar",
            "is_active",
        ]

    def update(self, instance, validated_data):
        # Update only the allowed fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class RoomListSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(source="members.count", read_only=True)
    created_by = UserForRoomSerializer(read_only=True)
    room_avatar = serializers.ImageField(use_url=True, required=False)


    class Meta:
        model = Room
        fields = ["id", "name", "description", "room_avatar", "created_by","created_at", "updated_at", "members_count"]
        read_only_fields = ["created_by", "created_at", "updated_at", "members_count"]
