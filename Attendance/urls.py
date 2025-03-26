from django.urls import path
from .views import CheckInView, CheckOutView, Last49DaysAttendanceView

urlpatterns = [
    path('checkin/', CheckInView.as_view(), name='attendance-checkin'),
    path('checkout/', CheckOutView.as_view(), name='attendance-checkout'),
    path('weekly/', Last49DaysAttendanceView.as_view(), name='weekly-attendance'),

]
