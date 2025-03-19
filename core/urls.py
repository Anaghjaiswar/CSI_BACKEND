from django.contrib import admin
from django.urls import path, include
from .views import warm_up

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
]
