from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from asapcutapp.models import University
from django.contrib.auth.decorators import login_required

@login_required

def university_list(request):
    universities = University.objects.all()

    return render(request, 'pages/universities/university_list.html', {'universities': universities})


def add_university(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        abbr = request.POST.get('abbr')
        error_message = None

        if name and abbr:
            # Check if the university name or abbreviation already exists
            if University.objects.filter(name=name).exists():
                error_message = f"The university name '{name}' already exists."
            elif University.objects.filter(abbr=abbr).exists():
                error_message = f"The abbreviation '{abbr}' is already in use."
            else:
                try:
                    University.objects.create(name=name, abbr=abbr)
                    messages.success(request, 'University added successfully.')
                    return redirect('university_list')
                except IntegrityError as e:
                    error_message = f"An error occurred: {e}"

        # Handle error cases by passing the error message back to the template
        if not name or not abbr:
            error_message = "All fields are required."

        universities = University.objects.all()
        return render(request, 'pages/universities/university_list.html', {
            'universities': universities,
            'add_error': error_message,  # Pass the error to the template
            'show_add_modal': True,      # Ensure the modal stays open
        })

    return redirect('university_list')


def update_university(request, id):
    university = get_object_or_404(University, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        abbr = request.POST.get('abbr')
        error_message = None

        if name and abbr:
            # Check for duplicate name and abbreviation
            if University.objects.filter(name=name).exclude(id=id).exists():
                error_message = f"The university name '{name}' already exists."
            elif University.objects.filter(abbr=abbr).exclude(id=id).exists():
                error_message = f"The abbreviation '{abbr}' is already in use."
            else:
                try:
                    university.name = name
                    university.abbr = abbr
                    university.save()
                    messages.success(request, 'University updated successfully.')
                    return redirect('university_list')
                except IntegrityError as e:
                    error_message = f"An error occurred: {e}"

        else:
            error_message = "All fields are required."

        # Return to the same page with error, keeping the modal open
        universities = University.objects.all()
        return render(request, 'pages/universities/university_list.html', {
            'universities': universities,
            'update_error': error_message,
            'show_update_modal': university.id,  # Indicate which modal to open
        })

    return redirect('university_list')


def delete_university(request, id):
    university = get_object_or_404(University, id=id)
    university.delete()
    messages.success(request, 'University deleted successfully')
    return redirect('university_list')