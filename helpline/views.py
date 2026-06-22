from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Helpline

@login_required
def helpline_list(request):
    category = request.GET.get('category', '')
    helplines = Helpline.objects.filter(is_active=True)
    if category:
        helplines = helplines.filter(category=category)
    categories = Helpline.CATEGORY_CHOICES
    return render(request, 'helpline/list.html', {
        'helplines': helplines,
        'categories': categories,
        'selected_category': category,
    })
