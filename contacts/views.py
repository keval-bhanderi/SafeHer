from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EmergencyContact
from .forms import EmergencyContactForm

@login_required
def contact_list(request):
    contacts = EmergencyContact.objects.filter(user=request.user)
    return render(request, 'contacts/list.html', {'contacts': contacts})

@login_required
def contact_add(request):
    if EmergencyContact.objects.filter(user=request.user).count() >= 5:
        messages.warning(request, 'You can only add up to 5 emergency contacts.')
        return redirect('contacts:list')
    if request.method == 'POST':
        form = EmergencyContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            messages.success(request, f'{contact.name} added as emergency contact!')
            return redirect('contacts:list')
    else:
        form = EmergencyContactForm()
    return render(request, 'contacts/form.html', {'form': form, 'action': 'Add'})

@login_required
def contact_edit(request, pk):
    contact = get_object_or_404(EmergencyContact, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EmergencyContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact updated!')
            return redirect('contacts:list')
    else:
        form = EmergencyContactForm(instance=contact)
    return render(request, 'contacts/form.html', {'form': form, 'action': 'Edit'})

@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(EmergencyContact, pk=pk, user=request.user)
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Contact removed.')
        return redirect('contacts:list')
    return render(request, 'contacts/confirm_delete.html', {'contact': contact})
