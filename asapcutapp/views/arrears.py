from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from xhtml2pdf import pisa
import openpyxl
from io import BytesIO
from collections import defaultdict
from ..models.organization_model import Contribution

def arrears_list(request):
    all_contributions = Contribution.objects.all()

    total_arrears_by_association = defaultdict(int)
    grand_total = 0

    for contribution in all_contributions:
        abbr = contribution.association.abbr
        total_arrears_by_association[abbr] += contribution.balance
        grand_total += contribution.balance

    total_arrears_by_association = dict(sorted(total_arrears_by_association.items()))

    context = {
        'total_arrears_by_association': total_arrears_by_association,
        'grand_total_arrears': grand_total,
        'has_arrears': bool(total_arrears_by_association),
    }

    return render(request, 'pages/arrears/manage_arrears.html', context)



def download_pdf(request):
    # load same data
    all_contributions = Contribution.objects.all()
    total_arrears_by_association = defaultdict(int)
    for c in all_contributions:
        total_arrears_by_association[c.association.abbr] += c.balance

    total_arrears_by_association = dict(sorted(total_arrears_by_association.items()))
    grand_total_arrears = sum(total_arrears_by_association.values())

    template_path = 'pages/arrears/pdf_template.html'
    context = {
        'total_arrears_by_association': total_arrears_by_association,
        'grand_total_arrears': grand_total_arrears
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="arrears_report.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response


def download_excel(request):
    all_contributions = Contribution.objects.all()
    total_arrears_by_association = defaultdict(int)
    for c in all_contributions:
        total_arrears_by_association[c.association.abbr] += c.balance

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Arrears Report"

    # Header
    ws.append(["#", "Association", "Total Arrears"])

    # Data rows
    for idx, (abbr, total) in enumerate(sorted(total_arrears_by_association.items()), 1):
        ws.append([idx, abbr, total])

    # Total
    ws.append(["", "Grand Total", sum(total_arrears_by_association.values())])

    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="arrears_report.xlsx"'
    wb.save(response)
    return response