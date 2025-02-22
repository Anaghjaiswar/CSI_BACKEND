from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    gallery_files = serializers.SerializerMethodField(read_only=True)
    poster = serializers.ImageField(use_url=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'guidelines', 'venue', 
            'registration_start_date', 'registration_end_date', 
            'event_date', 'poster', 'status', 'is_registrations_open', 
            'payment_required', 'amount', 'created_at', 'updated_at', 
            'gallery_files'
        ]  


    def get_gallery_files(self, obj):
        return [media.file.url for media in obj.gallery.all()]
    

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

