from django.urls import path
from .views import TaskCreateAPIView, EditTaskAPIView, DeleteTaskAPIView, TaskListAPIView, UserTasksAPIView

urlpatterns =[
    path('create/', TaskCreateAPIView.as_view(), name='task-create'),
    path('edit/<int:pk>/', EditTaskAPIView.as_view(), name='task-edit'),
    path('delete/<int:pk>/', DeleteTaskAPIView.as_view(), name='task-delete'),
    path('list/', TaskListAPIView.as_view(), name='task-list'),
    path('my-tasks/', UserTasksAPIView.as_view(), name='user-tasks'),
]