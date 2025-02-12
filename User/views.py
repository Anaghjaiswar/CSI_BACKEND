from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model  # Use this instead of directly importing User
from .serializers import  RegisterSerializer, UserListSerializer
from .models import PasswordResetOTP
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.crypto import get_random_string
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
import random

User = get_user_model()

class RegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Auto-generate a password
            generated_password = get_random_string(length=8)  # 8-character random password
            
            # Create the user
            validated_data = serializer.validated_data
            user = User.objects.create(
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
            )
            user.set_password(generated_password)  # Set the generated password
            user.save()

            # Send email with the password and welcome message
            subject = "Welcome to CSI App! Your Account Details"
            message = (
                f"Dear {user.first_name} {user.last_name},\n\n"
                # f"Thank you for registering with the CSI Technical Society at AKGEC, Ghaziabad.\n\n"
                f"Our team warmly welcomes you to an exciting journey of innovation, learning, "
                f"and collaboration. We're thrilled to have you as part of our community.\n\n"
                f"Here are your account details:\n"
                f"Email: {user.email}\n"
                f"Password: {generated_password}\n\n"
                f"Use this password to log in to your account.\n\n"
                f"Warm regards,\n\n"
                f"Team CSI\n"
                f"AKGEC, Ghaziabad\n"
            )
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            send_mail(subject, message, email_from, recipient_list)

            return Response(
                {"message": "User registered successfully. Login details and welcome message have been sent via email."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(ObtainAuthToken):
    """
    API for user login.
    """
    def post(self, request, *args, **kwargs):
        # Extract credentials
        email = request.data.get("email")
        password = request.data.get("password")

        # Authenticate user
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid email or password.")

        # Check if token already exists, create if not
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "message": f"Welcome {user.first_name}!"
        })


class CustomLogoutView(APIView):
    """
    API for user logout.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the token to invalidate it
        request.auth.delete()
        return Response({"message": "Successfully logged out."})


class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]


class ForgotPasswordOTPAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            # Generate a 6-digit OTP
            otp = f"{random.randint(100000, 999999)}"
            PasswordResetOTP.objects.create(user=user, otp=otp)

            # Send the OTP via email
            send_mail(
                "Your Password Reset OTP",
                f"Hi {user.first_name},\n\nYour OTP for resetting your password is: {otp}\n\n"
                f"This OTP is valid for 10 minutes.\n\n"
                f"If you did not request this, please ignore this email.",
                "no-reply@example.com",
                [user.email],
                fail_silently=False,
            )

            return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordWithOTPAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("password")

        if not email or not otp or not new_password:
            return Response({"error": "Email, OTP, and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = get_object_or_404(User, email=email)
            otp_record = PasswordResetOTP.objects.filter(user=user, otp=otp, is_used=False).first()

            if not otp_record or not otp_record.is_valid():
                return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

            # Reset the password
            user.set_password(new_password)
            user.save()

            # Mark the OTP as used
            otp_record.is_used = True
            otp_record.save()

            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
