from django.urls import path
from .views import CreateEventAPIView, EditEventAPIView, DeleteEventAPIView, EventHomeAPIView, EventDetailAPIView, EventListView

urlpatterns = [
    path('create/', CreateEventAPIView.as_view(), name='create-event'),
    path('edit/<int:id>/', EditEventAPIView.as_view(), name='edit-event'),
    path('delete/<int:id>/', DeleteEventAPIView.as_view(), name='delete-event'),
    path('event-for-homepage/', EventHomeAPIView.as_view(), name='event-for-homepage'),
    path('detail/<int:event_id>/', EventDetailAPIView.as_view(), name='event-detail'),
    path('list/', EventListView.as_view(), name='event-list'),
]