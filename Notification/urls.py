from django.urls import path
from .views import MarkNotificationsReadAPIView, UnreadNotificationCountAPIView

urlpatterns = [
    path('mark-as-read/', MarkNotificationsReadAPIView.as_view(), name='mark-as-read'),
    path('unread-count/', UnreadNotificationCountAPIView.as_view(), name='unread-count'),
]