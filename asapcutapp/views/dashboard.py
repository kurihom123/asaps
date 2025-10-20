from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from asapcutapp.models import University, Association, Contribution


@login_required
def dashboard(request):
    total_universities = University.objects.count()
    total_associations = Association.objects.count()
    total_contributions = Contribution.objects.filter(amount_paid__gt=0).count() 
    total_members = Association.objects.aggregate(total_members=Sum('member_number'))['total_members'] or 0

    context = {
        'total_universities': total_universities,
        'total_associations': total_associations,
        'total_contributions': total_contributions,
        'total_members': total_members
    }
    return render(request, 'pages/base.html', context)
