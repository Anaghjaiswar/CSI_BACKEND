from django.urls import path
from .views import AnnouncementCreateAPIView

urlpatterns = [
    path('create/', AnnouncementCreateAPIView.as_view(), name='create-announcement'),
]
