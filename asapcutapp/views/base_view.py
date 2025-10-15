from django.shortcuts import render
from ..models.organization_model import Association
from ..models.user_model import UserProfile

def base(request):
     context = {
        'president': UserProfile.objects.filter(position__name__icontains='President').first(),
        'vice_president': UserProfile.objects.filter(position__name__icontains='Vice President').first(),
        'general_secretary': UserProfile.objects.filter(position__name__icontains='General Secretary').first(),
        'treasurer': UserProfile.objects.filter(position__name__icontains='Treasurer').first(),
        'deputy_secretary': UserProfile.objects.filter(position__name__icontains='Deputy Secretary').first(),
        'associations': Association.objects.all(),
    }
    return render(request, 'index.html', context)
