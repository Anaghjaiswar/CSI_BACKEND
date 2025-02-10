from django.urls import path
from .views import EventListView, EventDetailView

urlpatterns = [
    path('list/', EventListView.as_view(), name='event-list'),
    path('<int:id>/', EventDetailView.as_view(), name='event-detail'),
]
