from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from asapcutapp.models import Association, University
from django.contrib.auth.decorators import login_required

@login_required

def association_list(request):
    associations = Association.objects.select_related('university').all()
    universities = University.objects.all()  # Needed for the dropdown in the modal
    return render(request, 'pages/associations/association_list.html', {
        'associations': associations,
        'universities': universities
    })


def add_association(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        abbr = request.POST.get('abbr')
        member_number = request.POST.get('member_number')
        university_id = request.POST.get('university_id')
        logo = request.FILES.get('logo')
        error_message = None

        if name and abbr and member_number and university_id:
            try:
                university = University.objects.get(id=university_id)
                Association.objects.create(
                    name=name,
                    abbr=abbr,
                    member_number=member_number,
                    university=university,
                    logo=logo
                )
                messages.success(request, 'Association added successfully.')
                return redirect('association_list')
            except University.DoesNotExist:
                error_message = "Selected university does not exist."
            except IntegrityError as e:
                error_message = f"An error occurred: {e}"
        else:
            error_message = "All fields are required."

        associations = Association.objects.select_related('university').all()
        universities = University.objects.all()
        return render(request, 'pages/associations/association_list.html', {
            'associations': associations,
            'universities': universities,
            'add_error': error_message,
            'show_add_modal': True
        })
    return redirect('association_list')


def update_association(request, id):
    association = get_object_or_404(Association, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        abbr = request.POST.get('abbr')
        member_number = request.POST.get('member_number')
        university_id = request.POST.get('university_id')
        logo = request.FILES.get('logo')
        error_message = None

        if name and abbr and member_number and university_id:
            try:
                university = University.objects.get(id=university_id)
                association.name = name
                association.abbr = abbr
                association.member_number = member_number
                association.university = university
                if logo:
                    association.logo = logo
                association.save()
                messages.success(request, 'Association updated successfully.')
                return redirect('association_list')
            except University.DoesNotExist:
                error_message = "Selected university does not exist."
            except IntegrityError as e:
                error_message = f"An error occurred: {e}"
        else:
            error_message = "All fields are required."

        associations = Association.objects.select_related('university').all()
        universities = University.objects.all()
        return render(request, 'pages/associations/association_list.html', {
            'associations': associations,
            'universities': universities,
            'update_error': error_message,
            'show_update_modal': association.id
        })

    return redirect('association_list')


def delete_association(request, id):
    association = get_object_or_404(Association, id=id)
    association.delete()
    messages.success(request, 'Association deleted successfully')
    return redirect('association_list')
