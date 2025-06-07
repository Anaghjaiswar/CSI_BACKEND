from rest_framework import serializers
from .models import User
from Domain.models import Domain
from django.contrib.auth import authenticate
from django.core.validators import MinLengthValidator
from rest_framework import serializers
from .models import User, StudentProfile, PasswordResetOTP
import random
from django.contrib.auth.models import Group
    

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['id','name']


class UserSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(use_url=True)
    domain = DomainSerializer()
    class Meta:
        model = User
        fields = ['id','first_name','last_name', 'domain','photo','year']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name','year']


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'role', 'year']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"



class MeetMyTeamUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    photo = serializers.ImageField(use_url=True)
    domain = DomainSerializer()

    class Meta:
        model = User
        fields = ['id', 'photo', 'full_name', 'domain']

    def get_full_name(self, obj):
        return obj.get_full_name()        


class UserProfileFillSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(use_url=True)
    domain = serializers.SlugRelatedField(
        queryset=Domain.objects.all(),  
        slug_field='name'               
    )
    
    class Meta:
        model = User
        fields = [
            'photo',
            'branch',
            'domain',  
            'dob',
            'linkedin_url',
            'bio',
            'github_url',
            'achievements',
            'hosteller',
        ]

class StudentRegistrationSerializer(serializers.Serializer):
    full_name    = serializers.CharField(max_length=150, write_only=True)
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        validators=[MinLengthValidator(8)],
        style={'input_type': 'password'}
    )
    branch = serializers.ChoiceField(choices=StudentProfile.BRANCH_CHOICES)
    year = serializers.ChoiceField(choices=StudentProfile.YEAR_CHOICES)
    student_number = serializers.CharField(max_length=50)
    hosteller = serializers.BooleanField()
    gender = serializers.ChoiceField(choices=StudentProfile.GENDER_CHOICES)

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        parts     = full_name.strip().split(' ', 1)
        first_name = parts[0]
        last_name  = parts[1] if len(parts) > 1 else ''
        branch = validated_data.pop('branch')
        year = validated_data.pop('year')
        student_number = validated_data.pop('student_number')
        hosteller = validated_data.pop('hosteller')
        gender = validated_data.pop('gender')

        email = validated_data.get('email')
        try:
            user = User.objects.get(email=email)
            user.first_name = first_name
            user.last_name = last_name
            user.save(update_fields=['first_name', 'last_name'])
        except User.DoesNotExist:
           user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                **validated_data
            )


        student_group, _ = Group.objects.get_or_create(name="student")
        if not user.groups.filter(name="student").exists():
            user.groups.add(student_group)

        if hasattr(user, 'student_profile'):
            raise serializers.ValidationError({"detail": "Student profile already exists for this user."})

        StudentProfile.objects.create(
            user=user,
            branch=branch,
            year=year,
            student_number=student_number,
            hosteller=hosteller,
            gender=gender,
        )
        return user

    def to_representation(self, instance):
        return {
            'full_name': f"{instance.first_name} {instance.last_name}".strip(),
            'email': instance.email
        }

        
       
    
class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email address.")
        # Fetch the latest OTP record for email verification (could be different from password OTP)
        otp_obj = PasswordResetOTP.objects.filter(user=user, is_used=False).order_by('-created_at').first()
        if not otp_obj:
            raise serializers.ValidationError("OTP not found. Please request a new one.")
        if not otp_obj.is_valid():
            raise serializers.ValidationError("OTP expired or already used.")
        if otp_obj.otp != otp:
            raise serializers.ValidationError("Invalid OTP.")
        attrs['user'] = user
        attrs['otp_obj'] = otp_obj
        return attrs
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    


    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_verified:
            raise serializers.ValidationError("Please verify your email before logging in.")
        attrs['user'] = user
        return attrs
    
