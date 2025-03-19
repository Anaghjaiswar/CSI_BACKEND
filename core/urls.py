from django.contrib import admin
from django.urls import path, include
from .views import warm_up, HomepageEventsAPIView, HomepageAnnouncementsAPIView, HomepageCountsAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('User.urls')),
    path('api/event/', include('Event.urls')),
    path('api/media/', include('Media.urls')),
    path('api/chat/', include('Chat.urls')),
    path('api/domain/', include('Domain.urls')),
    path('api/task/', include('Task.urls')),
    path('api/warmup/', warm_up, name='warmup'),
    path('api/notifications/', include('Notification.urls')),
    path('api/attendance/', include('Attendance.urls')),
    path('api/announcement/', include('Announcement.urls')),
    path('api/homepage/events/',HomepageEventsAPIView.as_view()),
    path('api/homepage/announcements/',HomepageAnnouncementsAPIView.as_view()),
    path('api/homepage/stats/',HomepageCountsAPIView.as_view()),
]
