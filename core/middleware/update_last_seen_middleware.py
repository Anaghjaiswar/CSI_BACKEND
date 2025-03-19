# middleware.py
from django.utils import timezone

class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            # Update last_seen field with the current time
            request.user.last_seen = timezone.now()
            # Optionally, update only the last_seen field to minimize DB writes
            request.user.save(update_fields=['last_seen'])
        return response
