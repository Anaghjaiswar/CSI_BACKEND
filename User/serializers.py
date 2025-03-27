from rest_framework import serializers
from .models import User
from Domain.models import Domain
    

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
        fields = ['email', 'first_name', 'last_name']


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
    domain = DomainSerializer()
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