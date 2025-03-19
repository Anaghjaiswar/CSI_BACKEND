from rest_framework import serializers
from Event.models import Event
from Announcement.models import Announcement

class EventPosterSerializer(serializers.ModelSerializer):
    poster = serializers.ImageField(use_url=True)
    class Meta:
        model = Event
        fields = ['id', 'poster']


class AnnouncementHomepageSerializer(serializers.ModelSerializer):
    time_date = serializers.SerializerMethodField()
    related_to_display = serializers.SerializerMethodField()
    sender_first_name = serializers.CharField(source="sender.first_name", read_only=True)

    class Meta:
        model = Announcement
        fields = ['time_date', 'related_to_display', 'sender_first_name', 'message']

    def get_time_date(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")

    def get_related_to_display(self, obj):
        return obj.get_related_to_display()