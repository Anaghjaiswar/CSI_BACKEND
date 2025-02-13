from django.urls import path
from .views import (
    UserRoomsAPIView,
    RoomMembersAPIView,
    RoomMessagesAPIView,
)

urlpatterns = [
    path("rooms/", UserRoomsAPIView.as_view(), name="user-rooms"),
    path("rooms/<str:room_name>/members/", RoomMembersAPIView.as_view(), name="room-members"),
    path("rooms/<str:room_name>/messages/", RoomMessagesAPIView.as_view(), name="room-messages"),
]
