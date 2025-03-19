from rest_framework import serializers
from User.models import User
from .models import Domain


# need a serializer which seggregates the users on the basis of year and domain

class MemberSimpleSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name']

    def get_full_name(self, obj):
        # Using get_full_name method if available, otherwise constructing it.
        return obj.get_full_name()


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['id', 'name']
