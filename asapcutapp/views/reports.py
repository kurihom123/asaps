from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.contrib import messages
from django.db.models import Q
from asapcutapp.models import Report, ReportView
from django.utils import timezone
from ..forms import ReportUploadForm

@login_required
def report_list(request):
    user = request.user
    upload_form = ReportUploadForm()
    if request.method == "POST":
        upload_form = ReportUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            new_report = upload_form.save(commit=False)
            new_report.user = user
            new_report.save()
            messages.success(request, "Report uploaded successfully!")
            return redirect('report_list')
        else:
            messages.error(request, "Please check your form and try again.")

    # Handle Viewing (mark as viewed)
    report_id = request.GET.get("view_id")
    if report_id:
        report = Report.objects.filter(id=report_id).first()
        if report:
            ReportView.objects.get_or_create(user=user, report=report)
            return FileResponse(open(report.report_file.path, 'rb'), content_type='application/pdf')

    # Handle Download
    download_id = request.GET.get("download_id")
    if download_id:
        report = Report.objects.filter(id=download_id).first()
        if report:
            return FileResponse(open(report.report_file.path, 'rb'), as_attachment=True)

    # Reports + Unread logic
    reports = Report.objects.all().order_by('-created_at')
    viewed_reports = ReportView.objects.filter(user=user).values_list('report_id', flat=True)
    unread_reports = reports.exclude(id__in=viewed_reports)

    context = {
        'reports': reports,
        'unread_reports': unread_reports,
        'unread_ids': list(unread_reports.values_list('id', flat=True)),
        'upload_form': upload_form
    }

    return render(request, 'pages/reports/report_list.html', context)
