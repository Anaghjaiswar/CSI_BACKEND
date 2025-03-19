from rest_framework import serializers
from .models import Announcement

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = (
            'id',
            'sender',
            'receivers',
            'message',
            'related_to',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('sender', 'receivers', 'created_at', 'updated_at')
