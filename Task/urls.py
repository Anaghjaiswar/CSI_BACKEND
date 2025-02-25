from django.urls import path
from .views import TaskCreateAPIView, EditTaskAPIView, DeleteTaskAPIView

urlpatterns =[
    path('create/', TaskCreateAPIView.as_view(), name='task-create'),
    path('edit/<int:pk>/', EditTaskAPIView.as_view(), name='task-edit'),
    path('delete/<int:pk>/', DeleteTaskAPIView.as_view(), name='task-delete'),
]