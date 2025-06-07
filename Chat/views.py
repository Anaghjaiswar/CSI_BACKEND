from rest_framework.generics import CreateAPIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Room, Message, UserRoomStatus
from .serializers import MessageUploadSerializer, RoomSerializer, MessageSerializer, UserSerializer, EditRoomSerializer, RoomListSerializer
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Q
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

User = get_user_model()

class MarkRoomAsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        try:
            # print(2+2)
            room = get_object_or_404(Room, id=room_id)
            status_obj, created = UserRoomStatus.objects.get_or_create(user=request.user, room=room)
            status_obj.last_read = timezone.now()
            status_obj.save()
            return Response({"message": "Room marked as read."})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Display the groups or rooms the user has joined
class UserRoomsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            rooms = request.user.rooms.filter(is_active=True)
            if not rooms.exists():
                return Response({"message": "You have not joined any rooms."}, status=status.HTTP_404_NOT_FOUND)

            serializer = RoomSerializer(rooms, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# List of members in a particular group
class RoomMembersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        try:
            room = get_object_or_404(Room, id=room_id, is_active=True)
            serializer = UserSerializer(room.members.all(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MessagePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
class RoomMessagesAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    pagination_class = MessagePagination

    def get_queryset(self):
        room = get_object_or_404(Room, id=self.kwargs["room_id"], is_active=True)
        if self.request.user not in room.members.all():
            raise PermissionDenied("You are not a member of this room.")
        return room.messages.all().order_by("-created_at")


# 4. API for listing all groups not just groups that are joined by the user
class RoomListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rooms = Room.objects.filter(is_active=True)
        serializer = RoomListSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class CreateRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save(created_by=request.user)

            return Response(
                {"message": "Room created successfully", "room": RoomSerializer(room).data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id, *args, **kwargs):
        room = get_object_or_404(Room, id=room_id)

        # Check if the logged-in user is the creator of the room
        if room.created_by != request.user:
            return Response(
                {"error": "You are not authorized to delete this room."},
                status=status.HTTP_403_FORBIDDEN,
            )

        room.delete()
        return Response({"message": "Room deleted successfully."}, status=status.HTTP_200_OK)
    

class EditRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, room_id,):
        try:
            return Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise NotFound("Room not found")

    def put(self, request, room_id, *args, **kwargs):
        room = self.get_object(room_id)

        # Check if the user is a member of the room
        if not room.members.filter(id=request.user.id).exists():
            return Response(
                {"detail": "You do not have permission to edit this room."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EditRoomSerializer(instance=room, data=request.data, partial=True)
        if serializer.is_valid():
            updated_room = serializer.save()
            return Response(
                {
                    "message": "Room updated successfully",
                    "room": RoomSerializer(updated_room).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveYourselfFromRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, room_id):
        """
        Retrieve the Room object by its ID.
        """
        try:
            return Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise NotFound("Room not found")

    def post(self, request, room_id, *args, **kwargs):
        room = self.get_object(room_id)

        # Check if the user is a member of the room
        if not room.members.filter(id=request.user.id).exists():
            return Response(
                {"detail": "You are not a member of this room."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Restrict creator from leaving without transferring ownership
        if room.created_by == request.user:
            return Response(
                {"detail": "You are the group creator. Transfer ownership before leaving."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Remove the user from the room
        room.members.remove(request.user)
        return Response(
            {"message": "You have successfully removed yourself from the group."},
            status=status.HTTP_200_OK,
        )


class TransferOwnershipAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, room_id):
        return get_object_or_404(Room, id=room_id)

    def post(self, request, room_id, *args, **kwargs):
        room = self.get_object(room_id)

        # Ensure the requester is the current owner
        if room.created_by != request.user:
            return Response(
                {"detail": "Only the current owner can transfer ownership."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Validate the new owner ID
        new_owner_id = request.data.get("new_owner_id")
        if not new_owner_id:
            return Response(
                {"detail": "New owner ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            new_owner = room.members.get(id=new_owner_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "The specified user is not a member of this group."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update ownership
        room.created_by = new_owner
        room.save()

        return Response(
            {
                "message": "Ownership transferred successfully.",
                "new_owner": {"id": new_owner.id, "first_name": new_owner.first_name, "last_name": new_owner.last_name},
            },
            status=status.HTTP_200_OK,
        )

class AddYourselfToRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, room_id):
        return get_object_or_404(Room, id=room_id, is_active=True)

    def post(self, request, room_id, *args, **kwargs):
        room = self.get_object(room_id)

        # Check if the user is already a member
        if room.members.filter(id=request.user.id).exists():
            return Response(
                {"detail": "You are already a member of this group."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Add the user to the group
        room.members.add(request.user)
        room.save()

        return Response(
            {
                "message": "You have been added to the group successfully.",
                "room": {
                    "id": room.id,
                    "name": room.name,
                    "description": room.description,
                    "members": [
                        {"id": member.id, "first_name": member.first_name, "last_name": member.last_name}
                        for member in room.members.all()
                    ],
                    "created_by": {
                        "id": room.created_by.id,
                        "first_name": room.created_by.first_name,
                        "last_name": room.created_by.last_name,
                    },
                    "is_active": room.is_active,
                },
            },
            status=status.HTTP_200_OK,
        )
    
class UserGroupSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        groups = request.user.rooms.filter(is_active=True)
        if query:
            groups = groups.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        if not query:
            return Response(
                {"error": "Please Provide a search query."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not groups.exists():
            return Response(
                {"message": "No groups Found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = RoomListSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserGroupMembersSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id,*args, **kwargs ):
        room = get_object_or_404(Room, id=room_id, is_active=True)

        if not room.members.filter(id=request.user.id).exists():
            return Response(
                {"message": "You are not a member of this group"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        query = request.query_params.get('q', '')
        members = room.members.all()
        if query:
            members = members.filter(
                Q(first_name__icontains=query)|
                Q(last_name__icontains=query)
            )
        if not query:
            return Response(
                {"error": "Please Provide a search query."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not members.exists():
            return Response(
                {"message": "no user found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageUploadView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = MessageUploadSerializer

    def perform_create(self, serializer):
        room_id = self.kwargs["room_id"]
        room = get_object_or_404(Room, id=room_id, is_active=True)

        # ensure membership
        if self.request.user not in room.members.all():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Not a member of this room.")

        # save with explicit fields
        msg = serializer.save(
            room=room,
            sender=self.request.user,
            message_type=(
                "image" if serializer.validated_data["attachment"].content_type.startswith("image/")
                else "file"
            )
        )

        # broadcast over Channels
        channel_layer = get_channel_layer()
        payload = {
            "type":         "chat_message",
            "message":      msg.content,
            "attachment":   msg.attachment.url,
            "sender":       UserSerializer(msg.sender).data,
            "message_type": msg.message_type,
            "id":           msg.id,
            "created_at":   msg.created_at.isoformat(),
            "room":         room_id,
            "parent_message_id": getattr(msg.parent_message, "id", None),
        }
        async_to_sync(channel_layer.group_send)(f"chat_{room_id}", payload)

    def get_queryset(self):
        # not used, but needed for routing
        return Message.objects.none()