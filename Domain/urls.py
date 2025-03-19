from django.urls import path
from .views import DomainAndYearWiseUserAPIView,DomainsByYearAPIView

urlpatterns = [
    path('year-wise/', DomainAndYearWiseUserAPIView.as_view(), name='domain-year-wise'),
    path('each-year/',DomainsByYearAPIView.as_view(), name='dommain-year-list'),
]
