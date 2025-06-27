# broadcast_manager/views.py
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import ActivityLog

@login_required
@role_required('ADMIN', 'EDITOR')
def editor_dashboard(request):
    activity_logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'editor_dashboard.html', {'activity_logs': activity_logs})
    pass

@login_required
@role_required('ADMIN', 'PRODUCER')
def producer_control(request):
    activity_logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'producer_control.html', {'activity_logs': activity_logs})
    pass

@login_required
@role_required('ADMIN', 'FCC')
def fcc_operations(request):
    activity_logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'fcc_operations.html', {'activity_logs': activity_logs})
    pass

@login_required
def activity_logs(request):
    if not request.user.is_admin():
        return HttpResponseForbidden()
    
    logs = ActivityLog.objects.all().select_related('user')
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'activity_logs.html', {'page_obj': page_obj})