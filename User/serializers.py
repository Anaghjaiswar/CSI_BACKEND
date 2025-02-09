from rest_framework import serializers
from .models import User
from Domain.models import Domain

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    domain = serializers.SlugRelatedField(
        queryset=Domain.objects.all(),  # Queryset to search for the domain
        slug_field='name'  # Field in the Domain model to match the input string
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'photo', 'domain', 
                  'linkedin_url', 'insta_url', 'github_url', 'role', 
                  'bio', 'year', 'status', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
