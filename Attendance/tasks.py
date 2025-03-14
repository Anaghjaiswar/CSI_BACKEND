# from celery import shared_task
# from django.utils import timezone
# from datetime import datetime, time
# from .models import Attendance

# @shared_task
# def auto_checkout():
#     today = timezone.now().date()
#     # Define auto check-out time as 23:30 of the current day
#     auto_checkout_time = timezone.make_aware(datetime.combine(today, time(23, 30)))
    
#     # Fetch attendance records with a check-in time but no check-out time for today
#     records = Attendance.objects.filter(
#         date=today,
#         check_in_time__isnull=False,
#         check_out_time__isnull=True
#     )
#     count = records.count()
#     for record in records:
#         record.check_out_time = auto_checkout_time
#         record.save()
#     return f"Auto checkout completed for {count} records."
