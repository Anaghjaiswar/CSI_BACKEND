from django.urls import path
from .views import *


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
    path('profile/fill/', ProfileFillView.as_view(), name='profile-fill'),
    path('profile/detail/', ProfileDetailAPIView.as_view(), name='profile-detail'),
    path('student/register/', StudentRegistrationView.as_view(), name='student-registration'),
    path('student/verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('student/resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('student/login/', LoginView.as_view(), name='student-login'),
    path('student/forgot-password/', ForgotPasswordOTPAPIView.as_view(), name='student-forgot-password'),
    path('student/reset-password/', ResetPasswordWithOTPAPIView.as_view(), name='student-forgot-password'),
    path('student/logout/', LogoutView.as_view(), name='student-logout'),
]
