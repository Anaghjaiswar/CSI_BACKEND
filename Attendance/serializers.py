from rest_framework import serializers
from .models import Attendance

class CheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['check_in_latitude', 'check_in_longitude']
    
    def validate(self, data):
        lat = data.get('check_in_latitude')
        lon = data.get('check_in_longitude')
        
        if lat is None or not (-90 <= lat <= 90):
            raise serializers.ValidationError("Invalid latitude value. Must be between -90 and 90.")
        if lon is None or not (-180 <= lon <= 180):
            raise serializers.ValidationError("Invalid longitude value. Must be between -180 and 180.")
        return data


class CheckOutSerializer(serializers.Serializer):
    check_out_latitude = serializers.FloatField()
    check_out_longitude = serializers.FloatField()
