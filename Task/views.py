from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import json
from Notification.models import Notification
from Notification.utils import notify_user


class TaskCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        # Convert QueryDict to a plain dict (each key gets its first value)
        data = { key: request.data.get(key) for key in request.data }
        
        # DEBUG: Show plain dict
        # print("DEBUG plain data:", data)

        # Check and parse 'groups' if it's a string
        if 'groups' in data and isinstance(data['groups'], str):
            try:
                data['groups'] = json.loads(data['groups'])
            except json.JSONDecodeError:
                return Response(
                    {"groups": "Invalid JSON format for groups."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # DEBUG: Show parsed data after groups conversion
        # print("DEBUG parsed data:", data)

        serializer = TaskSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            task = serializer.save(assigned_by=request.user)
            task.refresh_from_db()

            # Iterate over each group in the task and send notifications to all its members
            for group in task.groups.all():
                for member in group.members.all():
                    # Create the notification record
                    notification = Notification.objects.create(
                        user=member,
                        event_type='task',
                        message=f"You have been assigned a new task: {task.title}",
                        is_read=False
                    )
                    # Prepare the payload for real-time delivery
                    notification_data = {
                        "id": notification.id,
                        "event_type": notification.event_type,
                        "message": notification.message,
                        "url": notification.url,
                        "created_at": notification.created_at.isoformat(),
                    }
                    # Use your utility function to send the notification via WebSocket
                    notify_user(member, notification_data)


            return Response(
                {
                    "message": "Task and groups created successfully!",
                    "task": TaskSerializer(task, context={'request': request}).data
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class EditTaskAPIView(APIView):
    """
    API View to edit an existing Task.
    - Only users with role "admin" (3rd or 4th year) can edit tasks.
    - 3rd-year admins cannot edit tasks that were created by 4th-year admins.
    - Uses PUT for full updates.
    - Groups provided in the payload will merge/update existing groups.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, pk, *args, **kwargs):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        # Permission checks:
        request_user = request.user
        if request_user.role != "admin":
            return Response({"error": "Only admin users can edit tasks."}, status=status.HTTP_403_FORBIDDEN)
        # If logged in user is 3rd year and task was assigned_by a 4th-year admin, disallow edit.
        if request_user.year == '3rd' and task.assigned_by.year == '4th':
            return Response({"error": "3rd-year admins cannot edit tasks assigned by 4th-year admins."},
                            status=status.HTTP_403_FORBIDDEN)

        # Convert QueryDict to plain dict for proper handling.
        data = {key: request.data.get(key) for key in request.data}
        # Handle groups field if provided as JSON string.
        if 'groups' in data and isinstance(data['groups'], str):
            try:
                data['groups'] = json.loads(data['groups'])
            except json.JSONDecodeError:
                return Response({"groups": "Invalid JSON format for groups."},
                                status=status.HTTP_400_BAD_REQUEST)
        # Debug logging (optional)
        print("DEBUG parsed data for update:", data)

        serializer = TaskSerializer(task, data=data, context={'request': request})
        if serializer.is_valid():
            updated_task = serializer.save()
            return Response({
                "message": "Task updated successfully!",
                "task": TaskSerializer(updated_task, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteTaskAPIView(APIView):
    """
    API View to delete an existing Task.

    Permissions:
      - Only admin users (3rd or 4th year) can delete tasks.
      - 2nd-year users are not permitted to delete tasks.
      - 3rd-year admins cannot delete tasks assigned by 4th-year admins.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        # Retrieve the task by its primary key.
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        # Permission Check: 
        if request.user.role != "admin":
            return Response({"error": "Only admin users can delete tasks."},
                            status=status.HTTP_403_FORBIDDEN)
        
        if request.user.year == '3rd' and task.assigned_by.year == '4th':
            return Response({"error": "3rd-year admins cannot delete tasks assigned by 4th-year admins."},
                            status=status.HTTP_403_FORBIDDEN)

        task.delete()
        return Response({"message": "Task deleted successfully!"}, status=status.HTTP_200_OK)
    
class TaskListAPIView(APIView):
    """
    API View to list all tasks.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserTasksAPIView(APIView):
    """
    API endpoint to fetch tasks for the logged-in user, grouped by status.

    A task is considered associated with the user if the user is a member
    of any group attached to that task.

    The response groups tasks into three categories:
      - "current": Tasks that are currently ongoing.
      - "pending": Tasks whose end date has passed and are not completed.
      - "completed": Tasks with 100% progress (or as computed).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get all tasks where the logged-in user is a member of any group.
        tasks = Task.objects.filter(groups__members=request.user).distinct()
   
        tasks_by_status = {
            "current": [],
            "pending": [],
            "completed": []
        }
        
        # Serialize each task and use the computed status (via get_status()).
        for task in tasks:
            serialized_task = TaskSerializer(task, context={'request': request}).data
            status_key = serialized_task.get("status")
            # Ensure the status key exists in our dictionary.
            if status_key not in tasks_by_status:
                tasks_by_status[status_key] = []
            tasks_by_status[status_key].append(serialized_task)
        
        return Response(tasks_by_status, status=status.HTTP_200_OK)