import openpyxl
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from ..models import Contribution, Association, ContributionFile

@login_required
def upload_contribution_excel(request):
    if request.method == 'POST':
        year = request.POST.get('year')
        excel_file = request.FILES['file']

        # Role-based restriction
        position = getattr(request.user.user_profile.position, 'name', '').lower()
        if position not in ['president', 'general secretary', 'treasurer']:
            messages.error(request, "You don't have permission to upload contribution data.")
            return redirect('contribution_list')

        # Save file record
        file_record = ContributionFile.objects.create(year=year, file=excel_file)

        wb = openpyxl.load_workbook(excel_file)
        ws = wb.active

        for row in ws.iter_rows(min_row=2, values_only=True):
            association_abbr, members, amount_paid, payment_date = row

            try:
                association = Association.objects.get(abbr=association_abbr)
            except Association.DoesNotExist:
                continue  # skip unknown associations

            allocation = int(members) * 500 * 12
            balance = allocation - int(amount_paid or 0)

            contribution, created = Contribution.objects.update_or_create(
                association=association,
                year=year,
                defaults={
                    'allocation': allocation,
                    'amount_paid': amount_paid or 0,
                    'balance': balance,
                    'payment_date': payment_date or None,
                }
            )

            # update member number if changed
            if association.member_number != members:
                association.member_number = members
                association.save()

        messages.success(request, f" Excel file for {year} uploaded and processed successfully!")
        return redirect('contribution_list')

    return redirect('contribution_list')
