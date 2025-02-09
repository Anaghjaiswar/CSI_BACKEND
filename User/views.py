from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model  # Use this instead of directly importing User
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny

User = get_user_model()

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            # Save user
            user = serializer.save()

            # Set `is_staff` for admin role
            if user.role == 'admin':
                user.is_staff = True
                user.save()

            # Send confirmation email
            send_mail(
                subject="Welcome to CSI App",
                message="Thank you for registering with CSI App.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    # permission_classes = [IsAuthenticated]  # Optional: Add authentication

    def get(self, request):
        users = User.objects.all()  # Fetch all users
        serializer = UserSerializer(users, many=True)  # Serialize user data
        return Response(serializer.data)