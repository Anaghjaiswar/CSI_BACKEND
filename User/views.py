from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model  # Use this instead of directly importing User
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()

class UserRegistrationView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            # Save user
            user = serializer.save()

            # Set `is_staff` for admin role
            if user.role == 'admin' or user.year in ['3rd', '4th']:
                user.is_staff = True
                user.save()

            # Send confirmation email
            send_mail(
                subject="Welcome to CSI App",
                 message=(
                    f"Dear {user.first_name} {user.last_name},\n\n"
                    f"Thank you for registering with the CSI Technical Society at AKGEC, Ghaziabad.\n\n"
                    f"Our team warmly welcomes you to an exciting journey of innovation, learning, "
                    f"and collaboration. We're thrilled to have you as part of our community.\n\n"
                    f"Warm regards,\n\n"
                    f"Team CSI\n"
                    f"AKGEC, Ghaziabad\n"
                ),
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