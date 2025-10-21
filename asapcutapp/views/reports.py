from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.contrib import messages
from django.db.models import Q
from asapcutapp.models import Report, ReportView
from django.utils import timezone
from ..forms import ReportUploadForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def report_list(request):
    user = request.user

    # Form
    upload_form = ReportUploadForm()

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

    # Reports
    reports = Report.objects.all().order_by('-created_at')

    # Prepare info for template
    reports_info = []
    for report in reports:
        viewed_by = ReportView.objects.filter(report=report).order_by('-viewed_at')
        user_viewed = viewed_by.filter(user=user).exists()
        # Users who have not viewed (exclude superusers)
        all_regular_users = User.objects.filter(is_superuser=False)
        not_viewed_users = all_regular_users.exclude(id__in=viewed_by.values_list('user_id', flat=True))
        reports_info.append({
            'report': report,
            'viewed_by_users': viewed_by,
            'user_viewed': user_viewed,
            'not_viewed_users': not_viewed_users
        })

    # Determine role safely
    profile = user.user_profile.first() if user.user_profile.exists() else None
    role_name = profile.position.name.lower() if profile else ''
    top_positions = ['president', 'general secretary', 'treasurer']

    context = {
        'reports_info': reports_info,
        'upload_form': upload_form,
        'role_name': role_name,
        'top_positions': top_positions,
    }
    return render(request, 'pages/reports/report_list.html', context)


@login_required
@require_POST
def mark_report_viewed(request, report_id):
    """
    This endpoint records that a user viewed a given report.
    """
    try:
        report = Report.objects.get(id=report_id)
        ReportView.objects.get_or_create(user=request.user, report=report)
        return JsonResponse({'status': 'success'})
    except Report.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Report not found'}, status=404)
    
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