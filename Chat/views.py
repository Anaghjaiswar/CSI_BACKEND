from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Room, Message
from .serializers import RoomSerializer, MessageSerializer, UserSerializer
from django.contrib.auth import get_user_model


User = get_user_model()

# Display the groups or rooms the user has joined
class UserRoomsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            rooms = request.user.rooms.filter(is_active=True)
            if not rooms.exists():
                return Response({"message": "You have not joined any rooms."}, status=status.HTTP_404_NOT_FOUND)

            serializer = RoomSerializer(rooms, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# List of members in a particular group
class RoomMembersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_name):
        try:
            room = get_object_or_404(Room, name=room_name, is_active=True)
            serializer = UserSerializer(room.members.all(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# API for displaying old messages of a particular group
class RoomMessagesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_name):
        try:
            room = get_object_or_404(Room, name=room_name, is_active=True)

            if request.user not in room.members.all():
                return Response(
                    {"error": "You are not a member of this room."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            messages = room.messages.filter(is_deleted=False).order_by("-created_at")[:50]
            if not messages.exists():
                return Response(
                    {"message": "No messages found in this room."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 4. API for listing all groups not just groups that are joined by the user
class RoomListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rooms = Room.objects.filter(is_active=True)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
