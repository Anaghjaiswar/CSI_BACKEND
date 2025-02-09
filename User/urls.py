from django.urls import path
from .views import UserRegistrationView,UserListView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('list/', UserListView.as_view(), name='user-list'),
]
