from django.urls import path
from .views import CreateEventAPIView, EditEventAPIView, DeleteEventAPIView

urlpatterns = [
    path('create/', CreateEventAPIView.as_view(), name='create-event'),
    path('edit/<int:id>/', EditEventAPIView.as_view(), name='edit-event'),
    path('delete/<int:id>/', DeleteEventAPIView.as_view(), name='delete-event'),
]