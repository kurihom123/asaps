from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin.index')
                elif user.is_staff and not user.is_superuser:
                    return redirect('dashboard')
                else:
                    return redirect('dashboard')
            # else:
            #     messages.error(request, 'Invalid username or password')
            #     return redirect('login')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    else:
        AuthenticationForm(request)

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')