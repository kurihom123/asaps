# views.py
from django.shortcuts import render, redirect
from ..models import Contribution
from ..forms import ContributionForm, ContributionFormYear
from django.db.models import Sum
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from xhtml2pdf import pisa

@login_required
def contribution_list(request):
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            member_number = contribution.association.member_number
            contribution.allocation = member_number * 500 * 12
            
            # Validate amount
            if contribution.amount_paid < 500:
                messages.error(request, "Amount paid cannot be less than 500/=.")
                return render(request, 'pages/contributions/contribution_list.html', {'form': form})
            elif contribution.amount_paid > contribution.allocation:
                messages.error(request, "Amount paid cannot exceed allocation.")
                return render(request, 'pages/contributions/contribution_list.html', {'form': form})
            
            # If valid, set balance and save
            contribution.balance = contribution.allocation - contribution.amount_paid
            contribution.save()
            messages.success(request, 'Contribution added successfully.')
            return redirect('contribution_list')
    else:
        form = ContributionForm()

    contributions = Contribution.objects.select_related('association').all().order_by('year')

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

    form_years = {}
    for year in grouped_contributions:
        form_years[year] = ContributionFormYear()
        
    context = {
        'grouped_contributions': dict(grouped_contributions),
        'total_members_by_year': total_members_by_year,
        'total_requested_by_year': total_requested_by_year,
        'total_allocation_by_year': total_allocation_by_year,
        'total_balance_by_year': total_balance_by_year,
        'form': form,
        'form_year': form_years,
    }
    return render(request, 'pages/contributions/contribution_list.html', context)


from xhtml2pdf import pisa

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

    # headers
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

    # adjust column width
    for col in ws.columns:
        max_length = max(len(str(cell.value)) for cell in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

    # export
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Contributions_{year}.xlsx'
    wb.save(response)
    return response

@login_required
def add_contribution_for_year(request, year):
    if request.method == 'POST':
        form = ContributionFormYear(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.year = year
            member_number = contribution.association.member_number
            contribution.allocation = member_number * 500 * 12

            if contribution.amount_paid < 500:
                form.add_error('amount_paid', "Amount paid cannot be less than 500/=")
            elif contribution.amount_paid > contribution.allocation:
                form.add_error('amount_paid', "Amount paid cannot exceed allocation.")
            else:
                contribution.balance = contribution.allocation - contribution.amount_paid
                contribution.save()
                messages.success(request, f"Contribution for {year} added successfully.")
                return redirect('contribution_list')

        # if form is not valid or has custom errors
        contributions = Contribution.objects.select_related('association').all().order_by('year')
        grouped_contributions = defaultdict(list)
        total_members_by_year = {}
        total_requested_by_year = {}
        total_allocation_by_year = {}

        for contribution in contributions:
            y = contribution.year
            grouped_contributions[y].append(contribution)
            total_members_by_year[y] = total_members_by_year.get(y, 0) + contribution.association.member_number
            total_requested_by_year[y] = total_requested_by_year.get(y, 0) + contribution.amount_paid
            total_allocation_by_year[y] = total_allocation_by_year.get(y, 0) + contribution.allocation

        form_years = {}
        for y in grouped_contributions:
            form_years[y] = ContributionFormYear()

        form_years[year] = form  # replace the form for the current year with the one containing errors

        return render(request, 'pages/contributions/contribution_list.html', {
            'grouped_contributions': dict(grouped_contributions),
            'total_members_by_year': total_members_by_year,
            'total_requested_by_year': total_requested_by_year,
            'total_allocation_by_year': total_allocation_by_year,
            'form': ContributionForm(),
            'form_year': form_years,
            'show_modal': year,  # Indicate which modal should be shown
        })
