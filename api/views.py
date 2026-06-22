from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from alerts.models import SOSAlert
from contacts.models import EmergencyContact
from nearby.models import NearbyResource
from helpline.models import Helpline
from notifications.utils import send_sos_notifications
from .serializers import (
    UserSerializer, RegisterSerializer, EmergencyContactSerializer,
    SOSAlertSerializer, NearbyResourceSerializer, HelplineSerializer
)
import math

# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

# ── Contacts ──────────────────────────────────────────────────────────────────

class ContactListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EmergencyContactSerializer

    def get_queryset(self):
        return EmergencyContact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if EmergencyContact.objects.filter(user=self.request.user).count() >= 5:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Maximum 5 emergency contacts allowed.")
        serializer.save(user=self.request.user)

class ContactDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmergencyContactSerializer

    def get_queryset(self):
        return EmergencyContact.objects.filter(user=self.request.user)

# ── Alerts ────────────────────────────────────────────────────────────────────

class TriggerSOSAPIView(APIView):
    def post(self, request):
        serializer = SOSAlertSerializer(data=request.data)
        if serializer.is_valid():
            alert = serializer.save(user=request.user)
            contacts = EmergencyContact.objects.filter(user=request.user)
            send_sos_notifications(alert, contacts)
            return Response({
                'success': True,
                'alert': SOSAlertSerializer(alert).data,
                'message': 'SOS alert triggered and contacts notified!'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AlertHistoryAPIView(generics.ListAPIView):
    serializer_class = SOSAlertSerializer

    def get_queryset(self):
        return SOSAlert.objects.filter(user=self.request.user)

class ResolveAlertAPIView(APIView):
    def post(self, request, pk):
        try:
            alert = SOSAlert.objects.get(pk=pk, user=request.user)
            alert.status = 'resolved'
            alert.resolved_at = timezone.now()
            alert.save()
            return Response({'success': True, 'message': 'Alert resolved.'})
        except SOSAlert.DoesNotExist:
            return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)

class UpdateLocationAPIView(APIView):
    def post(self, request, pk):
        try:
            alert = SOSAlert.objects.get(pk=pk, user=request.user, status='active')
            alert.latitude = request.data.get('latitude', alert.latitude)
            alert.longitude = request.data.get('longitude', alert.longitude)
            alert.save()
            return Response({'success': True})
        except SOSAlert.DoesNotExist:
            return Response({'error': 'Active alert not found'}, status=status.HTTP_404_NOT_FOUND)

# ── Nearby ────────────────────────────────────────────────────────────────────

class NearbyResourceAPIView(generics.ListAPIView):
    serializer_class = NearbyResourceSerializer

    def get_queryset(self):
        qs = NearbyResource.objects.filter(is_active=True)
        resource_type = self.request.query_params.get('type')
        city = self.request.query_params.get('city')
        if resource_type:
            qs = qs.filter(type=resource_type)
        if city:
            qs = qs.filter(city__icontains=city)
        return qs

class HelplineAPIView(generics.ListAPIView):
    serializer_class = HelplineSerializer

    def get_queryset(self):
        qs = Helpline.objects.filter(is_active=True)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs
