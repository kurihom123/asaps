from django.shortcuts import render, redirect
from ..models import Contribution, Association, ContributionUpload
from ..forms import ExcelUploadForm
from django.db.models import Sum
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from xhtml2pdf import pisa
import pandas as pd
from datetime import datetime

@login_required
def contribution_list(request):
    if request.method == 'POST' and 'excel_file' in request.FILES:
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            return handle_excel_upload(request, form)
    else:
        form = ExcelUploadForm()

    # Get all contributions ordered by year
    contributions = Contribution.objects.select_related('association').all().order_by('year')
    uploads = ContributionUpload.objects.all().order_by('-uploaded_at')

    grouped_contributions = defaultdict(list)
    total_members_by_year = {}
    total_requested_by_year = {}
    total_allocation_by_year = {}
    total_balance_by_year = {}

    for contribution in contributions:
        year = contribution.year
        grouped_contributions[year].append(contribution)

        # Initialize if not exists
        if year not in total_members_by_year:
            total_members_by_year[year] = 0
            total_requested_by_year[year] = 0
            total_allocation_by_year[year] = 0
            total_balance_by_year[year] = 0

        # Accumulate totals
        total_members_by_year[year] += contribution.association.member_number
        total_requested_by_year[year] += contribution.amount_paid
        total_allocation_by_year[year] += contribution.allocation
        total_balance_by_year[year] += contribution.balance

    context = {
        'grouped_contributions': dict(grouped_contributions),
        'total_members_by_year': total_members_by_year,
        'total_requested_by_year': total_requested_by_year,
        'total_allocation_by_year': total_allocation_by_year,
        'total_balance_by_year': total_balance_by_year,
        'upload_form': form,
        'uploads': uploads,
    }
    return render(request, 'pages/contributions/contribution_list.html', context)

def handle_excel_upload(request, form):
    """Process uploaded Excel file and update contributions"""
    excel_file = form.cleaned_data['excel_file']
    year = str(form.cleaned_data['year']).strip()

    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        df.columns = [str(col).strip() for col in df.columns]

        required_columns = ['Association', 'Members', 'Amount Paid']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            messages.error(request, f"Missing required columns: {', '.join(missing_columns)}")
            return redirect('contribution_list')

        updated_count = 0
        created_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                assoc_abbr = str(row['Association']).strip()
                members = int(row['Members'])
                amount_paid = float(row['Amount Paid'])
                payment_date = datetime.today().date()

                # Match association abbreviation
                try:
                    association = Association.objects.get(abbr=assoc_abbr)
                except Association.DoesNotExist:
                    errors.append(f"Association '{assoc_abbr}' not found")
                    continue

                # Update association member number if changed
                if association.member_number != members:
                    association.member_number = members
                    association.save()

                allocation = members * 500 * 12
                balance = allocation - amount_paid

                # Update or create contribution record
                obj, created = Contribution.objects.update_or_create(
                    association=association,
                    year=year,
                    defaults={
                        'allocation': allocation,
                        'amount_paid': amount_paid,
                        'balance': balance,
                        'payment_date': payment_date,
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
                continue

        # Save upload log
        upload = form.save(commit=False)
        upload.uploaded_by = request.user
        upload.save()

        # Show success message
        if created_count > 0 or updated_count > 0:
            messages.success(request, f"✅ Uploaded successfully for {year}. ({updated_count} updated, {created_count} new records)")
        else:
            messages.warning(request, f"No records were processed for {year}.")

        # Show errors if any
        if errors:
            for error in errors[:3]:  # Show only first 3 errors
                messages.warning(request, error)
            if len(errors) > 3:
                messages.warning(request, f"... and {len(errors) - 3} more errors")

    except Exception as e:
        messages.error(request, f"❌ Error processing Excel: {str(e)}")

    return redirect('contribution_list')

# Keep your existing PDF and Excel export functions
@login_required
def contributions_pdf(request, year):
    contributions = Contribution.objects.filter(year=year).select_related('association')
    total = contributions.aggregate(
        members=Sum('association__member_number'),
        paid=Sum('amount_paid'),
        allocation=Sum('allocation'),
        balance=Sum('balance'),
    )

    context = {
        'year': year,
        'contributions': contributions,
        'total': total,
    }

    template_path = 'pages/contributions/contribution_pdf.html'
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Contributions_{year}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('PDF generation error', status=500)

    return response

@login_required
def contributions_excel(request, year):
    contributions = Contribution.objects.filter(year=year).select_related('association')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Contributions {year}"

    headers = ['Association', 'Members', 'Amount Paid', 'Allocation', 'Payment Date', 'Balance']
    ws.append(headers)

    for contribution in contributions:
        ws.append([
            contribution.association.abbr,
            contribution.association.member_number,
            contribution.amount_paid,
            contribution.allocation,
            contribution.payment_date.strftime('%Y-%m-%d'),
            contribution.balance,
        ])

    for col in ws.columns:
        max_length = max(len(str(cell.value)) for cell in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Contributions_{year}.xlsx'
    wb.save(response)
    return response



@login_required
def my_contributions(request):
    """View contributions for the logged-in user's association"""
    user = request.user

    if user.is_staff:
        return redirect('contribution_list')  # Redirect staff to admin page

    association = getattr(user.user_profile.first(), 'association', None)
    if not association:
        return render(request, 'pages/contributions/my_contributions.html', {
            'error': "No association found for your account."
        })

    contributions = Contribution.objects.filter(association=association).order_by('-year')

    return render(request, 'pages/contributions/my_contributions.html', {
        'association': association,
        'contributions': contributions,
    })


@login_required
def my_arrears(request):
    """View arrears (balances) per year for the user's association"""
    user = request.user

    association = getattr(user.user_profile.first(), 'association', None)
    if not association:
        return render(request, 'pages/contributions/my_arrears.html', {
            'error': "No association found for your account."
        })

    contributions = Contribution.objects.filter(association=association).order_by('-year')
    total_arrears = sum(c.balance for c in contributions)

    return render(request, 'pages/contributions/my_arrears.html', {
        'association': association,
        'contributions': contributions,
        'total_arrears': total_arrears,
    })
