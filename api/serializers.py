from rest_framework import serializers
from accounts.models import User
from alerts.models import SOSAlert
from contacts.models import EmergencyContact
from nearby.models import NearbyResource
from helpline.models import Helpline

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone', 'city', 'state', 'role']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'city', 'state', 'password', 'password2']


    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data


    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ['id', 'name', 'phone', 'email', 'relationship', 'is_primary']

class SOSAlertSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = SOSAlert
        fields = ['id', 'user', 'latitude', 'longitude', 'address', 'status', 'message', 'triggered_at', 'resolved_at']
        read_only_fields = ['id', 'user', 'triggered_at']

class NearbyResourceSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = NearbyResource
        fields = ['id', 'name', 'type', 'type_display', 'phone', 'address', 'city', 'state', 'latitude', 'longitude']

class HelplineSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Helpline
        fields = ['id', 'name', 'number', 'category', 'category_display', 'description', 'available_24x7', 'state']
