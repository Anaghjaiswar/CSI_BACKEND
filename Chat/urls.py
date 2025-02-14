from django.urls import path
from .views import (
    UserRoomsAPIView,
    RoomMembersAPIView,
    RoomMessagesAPIView,
    RoomListAPIView,
    CreateRoomAPIView,
    DeleteRoomAPIView,
    EditRoomAPIView,
    RemoveYourselfFromRoomAPIView,
    TransferOwnershipAPIView,
    AddYourselfToRoomAPIView,
)

urlpatterns = [
    path("groups/", UserRoomsAPIView.as_view(), name="user-rooms"),
    path("groups/<str:room_name>/members/", RoomMembersAPIView.as_view(), name="room-members"),
    path("groups/<str:room_name>/messages/", RoomMessagesAPIView.as_view(), name="room-messages"),
    path("groups/list/", RoomListAPIView.as_view(), name="room-list"),
    path('create-group/', CreateRoomAPIView.as_view(), name='create-room'),
    path('delete-group/<int:room_id>/', DeleteRoomAPIView.as_view(), name='delete-room'),
    path('edit-group/<int:room_id>/', EditRoomAPIView.as_view(), name='edit-room'),
    path('group/<int:room_id>/remove-yourself/', RemoveYourselfFromRoomAPIView.as_view(), name='remove-yourself-from-room'),
    path('group/<int:room_id>/transfer-ownership/', TransferOwnershipAPIView.as_view(), name='transfer-ownership'),
    path('group/<int:room_id>/add-yourself/', AddYourselfToRoomAPIView.as_view(), name='add-yourself-to-room'),
]
