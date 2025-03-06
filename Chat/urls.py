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
    UserGroupSearchAPIView,
    UserGroupMembersSearchAPIView,
    MarkRoomAsReadAPIView
)

urlpatterns = [
    path("groups/", UserRoomsAPIView.as_view(), name="user-rooms"),
    path("groups/<str:room_id>/members/", RoomMembersAPIView.as_view(), name="room-members"),
    path("groups/<str:room_id>/messages/", RoomMessagesAPIView.as_view(), name="room-messages"),
    path("groups/list/", RoomListAPIView.as_view(), name="room-list"),
    path('create-group/', CreateRoomAPIView.as_view(), name='create-room'),
    path('delete-group/<int:room_id>/', DeleteRoomAPIView.as_view(), name='delete-room'),
    path('edit-group/<int:room_id>/', EditRoomAPIView.as_view(), name='edit-room'),
    path('group/<int:room_id>/remove-yourself/', RemoveYourselfFromRoomAPIView.as_view(), name='remove-yourself-from-room'),
    path('group/<int:room_id>/transfer-ownership/', TransferOwnershipAPIView.as_view(), name='transfer-ownership'),
    path('group/<int:room_id>/add-yourself/', AddYourselfToRoomAPIView.as_view(), name='add-yourself-to-room'),
    path('groups/search/', UserGroupSearchAPIView.as_view(), name='group-search'),
    path('groups/<int:room_id>/search/members/',UserGroupMembersSearchAPIView.as_view(), name='group-search-members'),
    path('groups/<int:room_id>/mark-as-read/',MarkRoomAsReadAPIView.as_view(), name='mark-as-read'),
]

