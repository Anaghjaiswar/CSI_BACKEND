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
    is_self = serializers.SerializerMethodField()
    

    class Meta:
        model = Message
        fields = '__all__' 

    def get_is_self(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            return obj.sender.id == request.user.id
        return False

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
    unread_count = serializers.SerializerMethodField()
    last_read_timestamp = serializers.SerializerMethodField()
    last_read_message_id = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'members', 'room_avatar', 'is_active','unread_count', 'last_read_timestamp','last_read_message_id','created_by', 'created_at', 'updated_at', 'last_message']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        room = Room.objects.create(**validated_data)
        room.members.set(members)  # Add members to the room
        return room
    
    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        return LastMessageSerializer(last_message).data if last_message else None
    
    def get_unread_count(self, obj):
        # Retrieve the current user from the serializer
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0

        user = request.user

        try:
            status = obj.user_statuses.get(user=user)
            last_read = status.last_read
        except Exception:
            last_read = None

        # If a last_read timestamp exists, count messages created after it
        if last_read:
            unread_count = obj.messages.filter(created_at__gt=last_read).exclude(sender=request.user).count()
        else:
            unread_count = obj.messages.count()

        return unread_count
    
    def get_last_read_timestamp(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            try:
                user_room_status = obj.user_statuses.get(user=request.user)
                return user_room_status.last_read
            except obj.user_statuses.model.DoesNotExist:
                return None
        return None
    
    def get_last_read_message_id(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            try:
                user_room_status = obj.user_statuses.get(user=request.user)
                last_read_timestamp = user_room_status.last_read
                if last_read_timestamp:
                    # Retrieve the latest message with created_at <= last_read timestamp
                    last_read_message = obj.messages.filter(
                        created_at__lte=last_read_timestamp
                    ).order_by('-created_at').first()
                    if last_read_message:
                        return last_read_message.id
            except obj.user_statuses.model.DoesNotExist:
                return None
        return None


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
