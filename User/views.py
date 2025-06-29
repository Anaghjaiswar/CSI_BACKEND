from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import status, generics
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model 
from .serializers import  RegisterSerializer, UserListSerializer, MeetMyTeamUserSerializer, UserSerializer, UserProfileFillSerializer
from .models import PasswordResetOTP, User
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.crypto import get_random_string
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
import random
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from decouple import config
from django.db.models import Q
from .serializers import (StudentRegistrationSerializer,
                          EmailVerificationSerializer, LoginSerializer)
from django.utils import timezone

User = get_user_model()

class RegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Auto-generate a password
            generated_password = get_random_string(length=8)  # 8-character random password
            
            # Create the user
            validated_data = serializer.validated_data
            year = validated_data.get('year')
            if year == '2nd':
                role = 'member'
            elif year in ['3rd', '4th']:
                role = 'admin'
 
            user = User.objects.create(
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                year=year,
                role=role,
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

        required_fields = {
            "photo": user.photo,
            "branch": user.branch,
            "domain": user.domain,
            "dob": user.dob,
            "linkedin_url": user.linkedin_url,
            "github_url": user.github_url,
            "bio": user.bio,
        }

        missing_fields = [field for field, value in required_fields.items() if not value]
        profile_completed = (len(missing_fields) == 0)
        user.is_completed = profile_completed
        user.save(update_fields=["is_completed"])


        return Response({
            "year": user.year,
            "token": token.key,
            "is_completed": user.is_completed,
            "missing_fields": missing_fields,
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

class MembersSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()

        if not query: 
            return Response(
                {"error":"please provide a search query"},status=status.HTTP_400_BAD_REQUEST
            )

        users=User.objects.filter(
            Q(first_name__icontains=query)|Q(last_name__icontains=query)
        )

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
        

class MeetOurTeamAPIView(APIView):
    # permission_classes =[IsAuthenticated]

    def get(self, request, *args, **kwargs):
        

        print(User.YEAR_CHOICES)
        try: 
            users_by_year = {}

            for year in User.YEAR_CHOICES:
                year_key = year[0]
                users_in_year = User.objects.filter(year=year_key, status='active').select_related('domain')
                
                user_data = MeetMyTeamUserSerializer(users_in_year, many=True).data
                if user_data:
                    users_by_year[year_key] = user_data

            return Response(users_by_year, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "An error occurred while processing the request.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

ANDROID_CLIENT_ID = config("GOOGLE_ANDROID_CLIENT_ID")
IOS_CLIENT_ID = config("GOOGLE_IOS_CLIENT_ID")

class StudentGoogleLoginAPIView(APIView):
    permission_classes = []  # Allow public access

    def post(self, request):
        id_token_str = request.data.get("id_token")
        if not id_token_str:
            return Response(
                {"error": "ID token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify the token without an audience, so we can inspect it first
            idinfo = id_token.verify_oauth2_token(id_token_str, google_requests.Request())
            audience = idinfo.get("aud")
            if audience not in [ANDROID_CLIENT_ID, IOS_CLIENT_ID]:
                raise ValueError("Invalid audience: " + str(audience))
        except Exception as e:
            return Response(
                {"error": f"Invalid Google ID token: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = idinfo.get("email")
        if not email or not email.endswith("@akgec.ac.in"):
            return Response(
                {"error": "Email must end with '@akgec.ac.in'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        first_name = idinfo.get("given_name", "")
        last_name = idinfo.get("family_name", "")

        # Create or update the student user
        user, created = User.objects.get_or_create(email=email, defaults={
            "first_name": first_name,
            "last_name": last_name,
            "role": "student",
            "username": email.split('@')[0],  # Simplistic username generation
        })
        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.role = "student"
            user.save()

        # Generate or retrieve DRF token for the user
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "message": "Student logged in successfully."},
            status=status.HTTP_200_OK
        )
    

class ProfileFillView(APIView):
    """
    POST endpoint to update profile details for the authenticated user.
    Accepts photo, branch, domain, dob, linkedin_url, bio, and github_url.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Use partial=True to update only the provided fields.
        serializer = UserProfileFillSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_data = serializer.data
            # Append additional fields from the registered user data.
            response_data['full_name'] = f"{request.user.first_name} {request.user.last_name}".strip()
            response_data['year'] = request.user.year
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProfileDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **args):
        user = request.user
        serializer = UserProfileFillSerializer(user)
        serializer_data = serializer.data
        serializer_data['full_name'] = f"{request.user.first_name} {request.user.last_name}".strip()
        serializer_data['year'] = request.user.year
        return Response(serializer_data, status=status.HTTP_200_OK)

class EditProfileDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileFillSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StudentRegistrationView(generics.CreateAPIView):
    serializer_class = StudentRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        otp_code = f"{random.randint(100000, 999999)}"
        PasswordResetOTP.objects.create(user=user, otp=otp_code)

        send_mail(
            'Your Email Verification OTP',
            f'Your OTP is {otp_code}. It is valid for 10 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,  # Set to False to raise errors if email sending fails
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            'message': 'Registration successful. Please verify your email using the OTP sent to your email.'
        }
        return response
    
class VerifyEmailView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        otp_obj = serializer.validated_data['otp_obj']
        otp_obj.is_used = True
        otp_obj.save(update_fields=['is_used'])
        user.is_active = True
        user.is_verified = True
        user.save(update_fields=['is_active', 'is_verified'])
        return Response({'message': 'Email verified successfully. Your account is now active.'}, status=status.HTTP_200_OK)
    

class ResendOTPView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email address.'}, status=status.HTTP_400_BAD_REQUEST)

        otp_code = f"{random.randint(100000, 999999)}"
        otp_obj = PasswordResetOTP.objects.create(user=user, otp=otp_code)
        send_mail(
            'Your Email Verification OTP',
            f'Your OTP is {otp_code}. It is valid for 10 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )
        return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']


        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'message': 'Login successful.'

        }, status=status.HTTP_200_OK)
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Delete the token to log the user out.
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)