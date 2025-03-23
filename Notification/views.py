# notifications/views.py
from .serializers import DeviceTokenSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Notification.models import Notification
from rest_framework import status


class MarkNotificationsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        # Get a list of notification IDs from the request or mark all as read
        notification_ids = request.data.get("notification_ids", None)
        if notification_ids:
            updated_count = Notification.objects.filter(
                id__in=notification_ids, user=request.user, is_read=False
            ).update(is_read=True)
        else:
            # If no specific IDs provided, mark all as read
            updated_count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

        return Response({"updated": updated_count})
    
class UnreadNotificationCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": unread_count})
    




class RegisterDeviceTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = DeviceTokenSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

