from django.urls import path
from .views import MarkNotificationsReadAPIView, UnreadNotificationCountAPIView, RegisterDeviceTokenView

urlpatterns = [
    path('mark-as-read/', MarkNotificationsReadAPIView.as_view(), name='mark-as-read'),
    path('unread-count/', UnreadNotificationCountAPIView.as_view(), name='unread-count'),
    path('register-device/', RegisterDeviceTokenView.as_view(), name='register-device'),
]