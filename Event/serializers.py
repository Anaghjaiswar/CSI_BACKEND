from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    media_files = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ['id','title', 'media_files']


    def get_media_files(self, obj):
        return [media.file.url for media in obj.media_files.all()]
    

from rest_framework import serializers
from .models import Event

class EventDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'status',
            'registration_date',
            'event_date',
            'location',
            'online_link',
            'organizers',
            'media_files',
            'is_registrations_open',
            'created_at',
            'updated_at',
        ]

    media_files = serializers.SerializerMethodField()
    organizers = serializers.SerializerMethodField()

    def get_media_files(self, obj):
        return [media.file.url for media in obj.media_files.all()]

    def get_organizers(self, obj):
        return [{"id": organizer.id, "name": f"{organizer.first_name} {organizer.last_name}"} for organizer in obj.organizers.all()]

