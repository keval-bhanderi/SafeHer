from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import NearbyResource
import math

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

@login_required
def nearby_list(request):
    resource_type = request.GET.get('type', '')
    city = request.GET.get('city', request.user.city)
    resources = NearbyResource.objects.filter(is_active=True)
    if resource_type:
        resources = resources.filter(type=resource_type)
    if city:
        resources = resources.filter(city__icontains=city)

    # Add distance if user provides coordinates
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    if lat and lng:
        try:
            lat, lng = float(lat), float(lng)
            resources_with_distance = []
            for r in resources:
                if r.latitude and r.longitude:
                    dist = haversine(lat, lng, float(r.latitude), float(r.longitude))
                    resources_with_distance.append((r, round(dist, 2)))
            resources_with_distance.sort(key=lambda x: x[1])
            return render(request, 'nearby/list.html', {
                'resources': resources_with_distance, 'with_distance': True,
                'type': resource_type, 'city': city
            })
        except ValueError:
            pass

    return render(request, 'nearby/list.html', {
        'resources': [(r, None) for r in resources],
        'with_distance': False, 'type': resource_type, 'city': city
    })
