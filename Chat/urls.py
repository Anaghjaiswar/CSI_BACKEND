from django.urls import path
from .views import (
    UserRoomsAPIView,
    RoomMembersAPIView,
    RoomMessagesAPIView,
    RoomListAPIView,
)

urlpatterns = [
    path("groups/", UserRoomsAPIView.as_view(), name="user-rooms"),
    path("groups/<str:room_name>/members/", RoomMembersAPIView.as_view(), name="room-members"),
    path("groups/<str:room_name>/messages/", RoomMessagesAPIView.as_view(), name="room-messages"),
    path("groups/list/", RoomListAPIView.as_view(), name="room-list"),
]
