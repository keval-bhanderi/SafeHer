from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import SOSAlert
from contacts.models import EmergencyContact
from notifications.utils import send_sos_notifications
import json

@login_required
def sos_trigger(request):
    if request.method == 'POST':
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        alert = SOSAlert.objects.create(
            user=request.user,
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            address=data.get('address', ''),
            message=data.get('message', ''),
        )
        # Send notifications to emergency contacts
        contacts = EmergencyContact.objects.filter(user=request.user)
        send_sos_notifications(alert, contacts)

        if request.content_type == 'application/json':
            return JsonResponse({'success': True, 'alert_id': str(alert.id), 'message': 'SOS Alert triggered!'})
        messages.error(request, '🚨 SOS Alert sent to your emergency contacts!')
        return redirect('alerts:detail', pk=alert.id)
    return redirect('dashboard:home')

@login_required
def alert_detail(request, pk):
    if request.user.role in ['admin', 'ngo']:
        alert = get_object_or_404(SOSAlert, pk=pk)
    else:
        alert = get_object_or_404(SOSAlert, pk=pk, user=request.user)
    return render(request, 'alerts/detail.html', {'alert': alert})

@login_required
def alert_resolve(request, pk):
    if request.user.role in ['admin', 'ngo']:
        alert = get_object_or_404(SOSAlert, pk=pk)
    else:
        alert = get_object_or_404(SOSAlert, pk=pk, user=request.user)

    if request.method == 'POST':
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        if request.user.role in ['admin', 'ngo']:
            alert.acknowledged_by = request.user
        alert.save()
        messages.success(request, 'Alert marked as resolved. Stay safe!')
        if request.user.role in ['admin', 'ngo']:
            return redirect('dashboard:admin')
        return redirect('alerts:history')
    return render(request, 'alerts/confirm_resolve.html', {'alert': alert})

@login_required
def alert_history(request):
    alerts = SOSAlert.objects.filter(user=request.user)
    return render(request, 'alerts/history.html', {'alerts': alerts})

@login_required
def update_location(request, pk):
    if request.method == 'POST':
        alert = get_object_or_404(SOSAlert, pk=pk, user=request.user)
        data = json.loads(request.body)
        alert.latitude = data.get('latitude', alert.latitude)
        alert.longitude = data.get('longitude', alert.longitude)
        alert.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
