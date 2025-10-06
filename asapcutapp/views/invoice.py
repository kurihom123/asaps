from datetime import datetime
from num2words import num2words
from django.shortcuts import render, redirect
from ..models import Contribution
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.template.loader import get_template

@login_required
def invoice_pdf(request, year):
    # Fetch contributions for the specified year
    contributions = Contribution.objects.filter(year=year).select_related('association')

    # Totals
    totals = contributions.aggregate(
        total_members=Sum('association__member_number'),
        total_paid=Sum('amount_paid'),
        total_allocation=Sum('allocation'),
        total_balance=Sum('balance'),
    )

    # Convert total balance to words (e.g., "Four Hundred Eighty Thousand Tanzanian Shillings")
    total_balance_value = totals['total_balance'] or 0
    balance_in_words = num2words(total_balance_value, lang='en').title() + " Tanzanian Shillings"

    # Generate invoice number
    invoice_count = Contribution.objects.filter(year=year).count()
    invoice_number = f"{invoice_count + 1:05d}/{year}"

    # Date
    current_date = datetime.now().strftime('%d %B %Y')

    context = {
        'year': year,
        'contributions': contributions,
        'totals': totals,
        'invoice_number': invoice_number,
        'current_date': current_date,
        'balance_in_words': balance_in_words,
    }

    # Render
    template = get_template('pages/contributions/invoice_template.html')
    html = template.render(context)

    # PDF Response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{year}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
