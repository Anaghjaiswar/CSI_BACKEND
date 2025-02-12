from django.urls import path
from .views import RegisterAPIView,CustomLoginView,CustomLogoutView,UserListView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='user-registration'),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path('list/', UserListView.as_view(), name='user-list'),
]
