from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.contrib import messages
from django.db.models import Q
from asapcutapp.models import Report, ReportView
from django.utils import timezone
from ..forms import ReportUploadForm

@login_required
def report_list(request):
    user = request.user
    upload_form = ReportUploadForm()

    # Detect role
    role_name = getattr(getattr(getattr(user, 'user_profile', None), 'first', None), 'position', None)
    role_name = getattr(role_name, 'name', '').lower() if role_name else ''

    # Handle POST upload
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

    # Handle Viewing
    view_id = request.GET.get("view_id")
    if view_id:
        report = Report.objects.filter(id=view_id).first()
        if report:
            ReportView.objects.get_or_create(user=user, report=report)
            messages.success(request, "You have viewed this document.")
            return FileResponse(open(report.report_file.path, 'rb'), content_type='application/pdf')

    # Handle Download
    download_id = request.GET.get("download_id")
    if download_id:
        report = Report.objects.filter(id=download_id).first()
        if report:
            return FileResponse(open(report.report_file.path, 'rb'), as_attachment=True)

    # Get reports and precompute viewed info
    reports = Report.objects.all().order_by('-created_at')
    reports_info = []
    for report in reports:
        viewed_by_ids = ReportView.objects.filter(report=report).values_list('user_id', flat=True)
        viewed_by_users = ReportView.objects.filter(report=report)
        # For regular user check if they viewed this report
        user_viewed = ReportView.objects.filter(report=report, user=user).exists()
        reports_info.append({
            'report': report,
            'viewed_by_users': viewed_by_users,
            'user_viewed': user_viewed,
        })

    context = {
        'reports_info': reports_info,
        'role_name': role_name,
        'upload_form': upload_form
    }
    return render(request, 'pages/reports/report_list.html', context)


@login_required
def add_report(request):
    user = request.user
    if request.method == "POST":
        form = ReportUploadForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = user
            report.save()
            messages.success(request, "Report uploaded successfully!")
        else:
            messages.error(request, "Please check your form and try again.")
    return redirect('report_list')


@login_required
def download_report(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        return FileResponse(
            open(report.report_file.path, 'rb'),
            as_attachment=True,
            filename=report.report_file.name.split('/')[-1],
            content_type='application/pdf'
        )
    except Report.DoesNotExist:
        raise Http404("Report does not exist")