from rest_framework import serializers
from .models import Task, Group
from User.models import User

class MemberSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    # Return the domain's name. Adjust if you need more details.
    domain = serializers.CharField(source='domain.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'domain']

    def get_full_name(self, obj):
        # Concatenate first and last name, handling None for last_name.
        return f"{obj.first_name} {obj.last_name or ''}".strip()
    

class GroupSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'members']

    def create(self, validated_data):
        """
        Create a group with the provided members.
        """
        members = validated_data.pop('members', [])
        group = Group.objects.create(**validated_data)
        group.members.set(members)
        return group
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Replace the 'members' field with detailed information using MemberSerializer
        rep['members'] = MemberSerializer(instance.members.all(), many=True, context=self.context).data
        return rep


class TaskSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    attachment = serializers.FileField(use_url=True, required=False)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'start_date',
            'end_date',
            'status',
            'current_progress',
            'attachment',
            'info_url',
            'groups',
        ]

    def validate(self, data):
        """
        Validate assigned_by and group members.
        """
        request_user = self.context['request'].user  # Logged-in user
        groups = data.get('groups', [])

        # Check if the user has a valid 'year'
        user_year = getattr(request_user, 'year', None)
        if not user_year:
            raise serializers.ValidationError("User's year information is required.")

        for group_data in groups:
            members = group_data.get('members', [])
            if user_year == '2nd':
                raise serializers.ValidationError("2nd-year users cannot assign tasks.")
            for member in members:
                if user_year == '3rd' and member.year != '2nd':
                    raise serializers.ValidationError(
                        f"3rd-year users can only assign tasks to 2nd-year users. Invalid member: {member.id}"
                    )
                if user_year == '4th' and member.year not in ['2nd', '3rd']:
                    raise serializers.ValidationError(
                        f"4th-year users can only assign tasks to 2nd or 3rd-year users. Invalid member: {member.id}"
                    )

        # Validate start and end dates
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError("End date cannot be earlier than start date.")
        return data

    def create(self, validated_data):
        """
        Create a task and its associated groups.
        """
        groups_data = validated_data.pop('groups', [])
        task = Task.objects.create(**validated_data)

        # Create groups and associate them with the task
        for group_data in groups_data:
            group = Group.objects.create(task=task, name=group_data['name'])
            group.members.set(group_data['members'])

        return task
    
    def update(self, instance, validated_data):
        # Update task fields
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.status = validated_data.get('status', instance.status)
        instance.current_progress = validated_data.get('current_progress', instance.current_progress)
        instance.info_url = validated_data.get('info_url', instance.info_url)
        if validated_data.get('attachment'):
            instance.attachment = validated_data.get('attachment')
        instance.save()

        groups_data = validated_data.get('groups')
        if groups_data is not None:
            # For each group provided in the payload, update or create
            payload_group_names = []
            for group_data in groups_data:
                group_name = group_data.get('name')
                payload_group_names.append(group_name)
                members = group_data.get('members', [])
                try:
                    group = instance.groups.get(name=group_name)
                    # Update existing group members (replace with provided list)
                    group.members.set(members)
                    group.save()
                except Group.DoesNotExist:
                    # Create new group for this task
                    group = Group.objects.create(task=instance, name=group_name)
                    group.members.set(members)
            instance.groups.exclude(name__in=payload_group_names).delete()

        return instance
