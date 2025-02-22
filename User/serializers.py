from rest_framework import serializers
from .models import User
from Domain.models import Domain
    

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

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['name']


class MeetMyTeamUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    photo = serializers.ImageField(use_url=True)
    domain = DomainSerializer()

    class Meta:
        model = User
        fields = ['id', 'photo', 'full_name', 'domain']

    def get_full_name(self, obj):
        return obj.get_full_name()


