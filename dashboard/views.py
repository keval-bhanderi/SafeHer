from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from alerts.models import SOSAlert
from contacts.models import EmergencyContact
from helpline.models import Helpline

@login_required
def home(request):
    user = request.user
    active_alert = SOSAlert.objects.filter(user=user, status='active').first()
    recent_alerts = SOSAlert.objects.filter(user=user).order_by('-triggered_at')[:5]
    contacts_count = EmergencyContact.objects.filter(user=user).count()
    total_alerts = SOSAlert.objects.filter(user=user).count()
    helplines = Helpline.objects.filter(is_active=True, category__in=['women', 'police'])[:4]
    return render(request, 'dashboard/home.html', {
        'active_alert': active_alert,
        'recent_alerts': recent_alerts,
        'contacts_count': contacts_count,
        'total_alerts': total_alerts,
        'helplines': helplines,
    })

@login_required
def admin_dashboard(request):
    if request.user.role not in ['admin', 'ngo']:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access Denied")
    all_alerts = SOSAlert.objects.all().order_by('-triggered_at')
    active_alerts = all_alerts.filter(status='active')
    total_users = request.user.__class__.objects.filter(role='user').count()
    return render(request, 'dashboard/admin.html', {
        'all_alerts': all_alerts[:20],
        'active_alerts': active_alerts,
        'total_users': total_users,
        'active_count': active_alerts.count(),
        'total_alerts': all_alerts.count(),
    })
