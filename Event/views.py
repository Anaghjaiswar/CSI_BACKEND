from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Event
from .serializers import EventSerializer, EventDetailSerializer, EventHomeSerializer
from rest_framework import viewsets
from Media.models import MediaFile
from django.shortcuts import get_object_or_404


class EventListView(ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventDetailView(RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventDetailSerializer
    lookup_field = 'id'  # Use 'id' to identify events

    def get(self, request, *args, **kwargs):
        try:
            event = self.get_object()  # Fetch the specific event
            serializer = self.get_serializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        # except Exception as e:
        #     return Response(
        #         {"error": "An error occurred while fetching the event details.", "details": str(e)},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )

# for creating event details
class CreateEventAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Only admin users can create events
        if getattr(request.user, 'role', None) != 'admin':
            return Response(
                {'detail': 'Only admin users can create events.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Copy request data and remove gallery key to avoid serializer issues
        event_data = request.data.copy()
        event_data.pop('gallery', None)
        
        # Retrieve multiple files from the gallery key
        gallery_files = request.FILES.getlist('gallery')

        serializer = EventSerializer(data=event_data)
        if serializer.is_valid():
            event = serializer.save()
            # Process each uploaded file
            for file in gallery_files:
                media_file = MediaFile.objects.create(
                    file=file,
                    title=file.name,
                    file_size=file.size,
                )
                event.gallery.add(media_file)

            return Response(
                {"success": "Event created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EditEventAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        # Retrieve the event object
        event = get_object_or_404(Event, id=kwargs.get('id'))

        # Ensure only admin users can edit the event
        if getattr(request.user, 'role', None) != 'admin':
            return Response(
                {'detail': 'Only admin users can edit events.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Copy the request data to handle gallery updates separately
        event_data = request.data.copy()
        gallery_files = request.FILES.getlist('gallery')
        
        # Remove 'gallery' from event data to prevent serializer issues
        event_data.pop('gallery', None)

        # Serialize and validate the event data
        serializer = EventSerializer(event, data=event_data, partial=True)
        if serializer.is_valid():
            event = serializer.save()

            # Handle gallery updates
            if gallery_files:
                # Clear the existing gallery if needed
                event.gallery.clear()
                for file in gallery_files:
                    media_file = MediaFile.objects.create(
                        file=file,
                        title=file.name,
                        file_size=file.size,
                    )
                    event.gallery.add(media_file)

            return Response(
                {"success": "Event updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  

class DeleteEventAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # Retrieve the event object
        event = get_object_or_404(Event, id=kwargs.get('id'))

        # Ensure only admin users can delete the event
        if getattr(request.user, 'role', None) != 'admin':
            return Response(
                {'detail': 'Only admin users can delete events.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Delete the event
        event.delete()
        return Response(
            {'success': 'Event deleted successfully.'},
            status=status.HTTP_200_OK
        )
    
class EventHomeAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try: 
            event = Event.objects.all().order_by('-created_at')
            serializer = EventHomeSerializer(event, many = True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event Not Found"},
                status = status.HTTP_404_NOT_FOUND
            )
        
class EventDetailAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, event_id, *args, **kwargs):
        try:
            event = Event.objects.get(id=event_id)
            serializer = EventDetailSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event Not Found"},
                status=status.HTTP_404_NOT_FOUND
            )
