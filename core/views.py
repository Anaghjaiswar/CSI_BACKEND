from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from Event.models import Event
from django.http import JsonResponse
from rest_framework.views import APIView
from .serializers import EventPosterSerializer, AnnouncementHomepageSerializer
from rest_framework import generics
from Announcement.models import Announcement 
from Task.models import Task
from Announcement.models import Announcement
from Chat.models import Room, UserRoomStatus
from django.db.models import Max


def warm_up(request):
    return JsonResponse({"message": "Server is warm!"})


class HomepageEventsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        ongoing_events = Event.objects.filter(status="ongoing")
        upcoming_events = Event.objects.filter(status="upcoming")
        
        serialized_ongoing = EventPosterSerializer(ongoing_events, many=True).data
        serialized_upcoming = EventPosterSerializer(upcoming_events, many=True).data
        
        response_data = {
            "ongoing_events": serialized_ongoing,
            "upcoming_events": serialized_upcoming
        }
        
        return Response(response_data, status=status.HTTP_200_OK)



class AnnouncementPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'  # Allow client to override, if needed
    max_page_size = 20

class HomepageAnnouncementsAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnnouncementHomepageSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return Announcement.objects.filter(receivers=user).order_by('-created_at')
    
class HomepageCountsAPIView(APIView):
    """
    Returns counts for the logged-in user:
      1. tasks_assigned: Number of tasks (pending and current) assigned to the user.
      2. chat_groups_with_unread: Number of chat groups where the user has unread messages.
      3. announcement_count: Total number of announcements intended for the user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        first_name = user.first_name

        # 1. Count tasks assigned to the user (only pending and current tasks)
        tasks_count = Task.objects.filter(
            groups__members=user,
            status__in=['pending', 'current']
        ).distinct().count()

        # 2. Count chat groups (rooms) with unread messages.
        # We'll retrieve rooms where the user is a member and annotate them with the latest message timestamp.
        rooms = Room.objects.filter(members=user).annotate(
            latest_message=Max('messages__created_at')
        )
        unread_chat_count = 0
        for room in rooms:
            try:
                # Get the user's last read time for this room.
                user_status = room.user_statuses.get(user=user)
                last_read = user_status.last_read
            except UserRoomStatus.DoesNotExist:
                # If no status record exists, consider the room as having unread messages.
                last_read = None

            # If the room has any messages and either the user hasn't read any message yet or
            # the latest message is more recent than the last read timestamp, count it as unread.
            if room.latest_message and (last_read is None or room.latest_message > last_read):
                unread_chat_count += 1

        # 3. Count announcements where the user is a receiver.
        announcements_count = Announcement.objects.filter(receivers=user).count()

        response_data = {
            "name": first_name,
            "tasks_assigned": tasks_count,
            "chat_groups_with_unread": unread_chat_count,
            "announcement_count": announcements_count,
        }

        return Response(response_data, status=status.HTTP_200_OK)