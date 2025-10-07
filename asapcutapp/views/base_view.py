from django.shortcuts import render
from ..models.organization_model import Association
from ..models.user_model import UserProfile
from django.contrib.auth.decorators import login_required

@login_required

def base(request):
    associations = Association.objects.all()
    leaders = UserProfile.objects.select_related('level', 'association', 'position').all()
    return render(request, 'index.html', {'associations': associations, 'leaders': leaders})
