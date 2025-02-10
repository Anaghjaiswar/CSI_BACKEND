from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Event
from .serializers import EventSerializer, EventDetailSerializer


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
