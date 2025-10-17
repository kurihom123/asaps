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

        total_members_by_year[year] = total_members_by_year.get(year, 0) + contribution.association.member_number
        total_requested_by_year[year] = total_requested_by_year.get(year, 0) + contribution.amount_paid
        total_allocation_by_year[year] = total_allocation_by_year.get(year, 0) + contribution.allocation
        total_balance_by_year[year] = total_balance_by_year.get(year, 0) + contribution.balance

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
    """Process uploaded Excel file and update or add contributions"""
    excel_file = form.cleaned_data['excel_file']
    year = form.cleaned_data['year']

    try:
        df = pd.read_excel(excel_file)
        required_columns = ['Association', 'Members', 'Amount Paid', 'Payment Date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            messages.error(request, f"Missing columns: {', '.join(missing_columns)}")
            return redirect('contribution_list')

        success_count = 0
        error_messages = []

        for index, row in df.iterrows():
            try:
                assoc_abbr = str(row['Association']).strip()
                members = int(row['Members'])
                amount_paid = float(row['Amount Paid'])
                payment_date = row['Payment Date']

                # Convert date string if necessary
                if isinstance(payment_date, str):
                    payment_date = datetime.strptime(payment_date, "%Y-%m-%d").date()

                try:
                    association = Association.objects.get(abbr=assoc_abbr)
                except Association.DoesNotExist:
                    error_messages.append(f"Association '{assoc_abbr}' not found.")
                    continue

                # Allocation per your formula
                allocation = members * 500 * 12

                # Try to find an existing record for this association & year
                contribution, created = Contribution.objects.get_or_create(
                    association=association,
                    year=year,
                    defaults={
                        'allocation': allocation,
                        'amount_paid': amount_paid,
                        'payment_date': payment_date,
                        'balance': allocation - amount_paid,
                    }
                )

                if not created:
                    # Update existing record instead of replacing
                    new_total_paid = contribution.amount_paid + amount_paid
                    contribution.amount_paid = new_total_paid
                    contribution.allocation = allocation
                    contribution.payment_date = payment_date
                    contribution.balance = allocation - new_total_paid
                    contribution.save()

                success_count += 1

            except Exception as e:
                error_messages.append(f"Row {index + 2}: {str(e)}")

        # Record upload
        upload = form.save(commit=False)
        upload.uploaded_by = request.user
        upload.save()

        # Show messages
        if success_count:
            messages.success(request, f" {success_count} records processed for {year}.")
        if error_messages:
            for msg in error_messages[:5]:
                messages.warning(request, msg)
            if len(error_messages) > 5:
                messages.warning(request, f"...and {len(error_messages) - 5} more issues found.")

    except Exception as e:
        messages.error(request, f"Error processing Excel: {str(e)}")

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

# Remove the add_contribution_for_year function