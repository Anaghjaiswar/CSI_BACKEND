from rest_framework import serializers
from .models import DeviceToken

class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ['device_token', 'device_type']

    def create(self, validated_data):
        # Associate the token with the authenticated user
        user = self.context['request'].user
        # Update or create a token for the user
        obj, created = DeviceToken.objects.update_or_create(
            user=user,
            device_token=validated_data['device_token'],
            defaults={'device_type': validated_data.get('device_type', DeviceToken.ANDROID)}
        )
        return obj