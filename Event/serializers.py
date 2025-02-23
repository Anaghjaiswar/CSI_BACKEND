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
    poster = serializers.ImageField(use_url=True)
    gallery_files = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'guidelines', 'venue',
            'registration_start_date', 'registration_end_date',
            'event_date', 'poster', 'status', 'gallery_files',
            'is_registrations_open', 'payment_required', 'amount',
            'created_at', 'updated_at'
        ]

    def get_gallery_files(self, obj):
        return [media.file.url for media in obj.gallery.all()]


class  EventHomeSerializer(serializers.ModelSerializer):
    poster = serializers.ImageField(use_url=True)

    class Meta:
        model = Event
        fields = [
            'id', 'poster', 'status'
        ]

