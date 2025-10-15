from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models.user_model import UserProfile


@login_required
def users_list(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, "You don't have a registered profile.")
        return redirect('home')

    allowed_positions = ['President', 'General Secretary', 'Treasurer']

    if user_profile.position.name not in allowed_positions:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    users = UserProfile.objects.select_related('user', 'level', 'association', 'position').all()
    context = {
        'users': users,
        'user_position': user_profile.position.name
    }
    return render(request, 'pages/users/users_list.html', context)
