from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import json


class TaskCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        # Convert QueryDict to a plain dict (each key gets its first value)
        data = { key: request.data.get(key) for key in request.data }
        
        # DEBUG: Show plain dict
        print("DEBUG plain data:", data)

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
        print("DEBUG parsed data:", data)

        serializer = TaskSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            task = serializer.save(assigned_by=request.user)
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