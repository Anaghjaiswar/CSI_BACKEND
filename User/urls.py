from django.urls import path
from .views import RegisterAPIView,CustomLoginView,CustomLogoutView,UserListView,ForgotPasswordOTPAPIView,ResetPasswordWithOTPAPIView, MeetOurTeamAPIView, StudentGoogleLoginAPIView, MembersSearchAPIView


urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='user-registration'),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path('list/', UserListView.as_view(), name='user-list'),
    path("forgot-password/", ForgotPasswordOTPAPIView.as_view(), name="forgot-password-otp"),
    path("reset-password/", ResetPasswordWithOTPAPIView.as_view(), name="reset-password-otp"),
    path("meet-our-team/", MeetOurTeamAPIView.as_view(), name="meet-our-team"),
    path('search/', MembersSearchAPIView.as_view(), name='search-users'),
    path('student/google-login/', StudentGoogleLoginAPIView.as_view(), name='student-google-login'),
]
