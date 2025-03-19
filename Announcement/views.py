from .utils import get_receiver_ids
from .models import Announcement
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated 
from .serializers import AnnouncementSerializer  
from .utils import get_receiver_ids  

class AnnouncementCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response(
                {"error": "Only admin users can create announcements."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Remove it so the serializer only sees the fields it expects.
        targeting_data = request.data.pop('targeting_data', None)
        
        serializer = AnnouncementSerializer(data=request.data)
        if serializer.is_valid():

            announcement = serializer.save(sender=request.user)
            
            # Compute the receiver IDs based on the related_to field and provided targeting data.
            if targeting_data:
                receiver_ids = get_receiver_ids(announcement.related_to, targeting_data)
                announcement.receivers.add(*receiver_ids)
            
            return Response(
                {"message": "Announcement has been sent to all required users."},
                status=status.HTTP_201_CREATED
            )        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
