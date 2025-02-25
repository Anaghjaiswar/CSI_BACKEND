from django.urls import path
from .views import DomainAndYearWiseUserAPIView

urlpatterns = [
    path('year-wise/', DomainAndYearWiseUserAPIView.as_view(), name='domain-year-wise'),
]
