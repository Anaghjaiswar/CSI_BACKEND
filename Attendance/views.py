from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Attendance
from .serializers import CheckInSerializer, CheckOutSerializer
from .utils import calculate_distance, LAB_LATITUDE, LAB_LONGITUDE, RADIUS_THRESHOLD

class CheckInView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CheckInSerializer(data=request.data)
        if serializer.is_valid():
            today = timezone.now().date()
            # Prevent multiple check-ins per day
            if Attendance.objects.filter(user=request.user, date=today).exists():
                return Response({'error': 'You have already checked in today.'}, status=status.HTTP_400_BAD_REQUEST)
            
            user_lat = serializer.validated_data.get('check_in_latitude')
            user_lon = serializer.validated_data.get('check_in_longitude')
            distance = calculate_distance(LAB_LATITUDE, LAB_LONGITUDE, user_lat, user_lon)
            within_range = distance <= RADIUS_THRESHOLD

            # Create attendance record

            if within_range:
                Attendance.objects.create(
                    user=request.user,
                    date=today,
                    check_in_time=timezone.now(),
                    check_in_latitude=user_lat,
                    check_in_longitude=user_lon,
                    check_in_within_range=True
                )
                message = "Check-in successful. Attendance marked!"
                return Response({'message': message, 'distance': distance}, status=status.HTTP_200_OK)
            else:
                message = f"Check-in failed. You are {distance:.2f} meters away from the lab."
                return Response({'error': message, 'distance': distance}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckOutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CheckOutSerializer(data=request.data)
        if serializer.is_valid():
            today = timezone.now().date()
            try:
                attendance = Attendance.objects.get(user=request.user, date=today)
            except Attendance.DoesNotExist:
                return Response({'error': 'No check-in record found for today.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if attendance.check_out_time:
                return Response({'error': 'You have already checked out today.'}, status=status.HTTP_400_BAD_REQUEST)

            user_lat = serializer.validated_data.get('check_out_latitude')
            user_lon = serializer.validated_data.get('check_out_longitude')
            # For check-out, we simply record the location without proximity check
            attendance.check_out_time = timezone.now()
            attendance.check_out_latitude = user_lat
            attendance.check_out_longitude = user_lon
            attendance.check_out_within_range = True  # You may always mark this as true for check-out
            attendance.save()

            message = "Check-out successful. See you tomorrow!"
            return Response({'message': message}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
