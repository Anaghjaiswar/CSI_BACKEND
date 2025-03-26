from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Attendance
from .serializers import CheckInSerializer, CheckOutSerializer, DailyAttendanceSerializer
from .utils import calculate_distance, LAB_LATITUDE, LAB_LONGITUDE, RADIUS_THRESHOLD
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView


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
    
class Last49DaysAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Today is the last day in the 49-day window
        today = timezone.now().date()
        # Start date is 48 days before today (inclusive of today makes 49 days)
        start_date = today - timedelta(days=48)
        
        # Generate a list for each day in the 49-day period
        days_list = []
        for i in range(49):
            day = start_date + timedelta(days=i)
            try:
                record = Attendance.objects.get(user=request.user, date=day)
                attended = bool(record.check_in_time)
            except Attendance.DoesNotExist:
                attended = False
            days_list.append({
                "date": day,
                "attended": attended,
            })
        
        # Split the 49 days into chunks of 7 days each
        pages = [days_list[i:i+7] for i in range(0, 49, 7)]
        # Reverse so that the latest 7 days (ending on today) become page 1
        pages.reverse()
        total_pages = len(pages)
        
        # Get the page number from query params (default to page 1)
        try:
            page = int(request.query_params.get('page', 1))
        except ValueError:
            return Response({"detail": "Invalid page number."}, status=400)
        
        if page < 1 or page > len(pages):
            return Response({"detail": "Page out of range."}, status=400)
        
        week_data = pages[page - 1]
        
        # For page 1 (the latest block) all days are <= today
        serializer = DailyAttendanceSerializer(week_data, many=True)
        
        # Determine month info for this page. If all days are in one month, include "month"
        # otherwise, return a list under "months".
        month_set = { day["date"].strftime('%B') for day in week_data }
        if len(month_set) == 1:
            month_info = {"month": month_set.pop()}
        else:
            month_info = {"months": list(month_set)}


        query_params = request.query_params.copy()

        # Build next URL if exists.
        if page < total_pages:
            query_params["page"] = page + 1
            next_url = f"https://csi-backend-wvn0.onrender.com/api/attendance/weekly/?{query_params.urlencode()}"
        else:
            next_url = None

        # Build previous URL if exists.
        if page > 1:
            query_params["page"] = page - 1
            previous_url = f"https://csi-backend-wvn0.onrender.com/api/attendance/weekly/?{query_params.urlencode()}"
        else:
            previous_url = None
        
        response_data = {
            "page": page,
            "total_pages": total_pages,
            "next": next_url,
            "previous": previous_url,
            "results": serializer.data,
        }
        response_data.update(month_info)
        return Response(response_data)