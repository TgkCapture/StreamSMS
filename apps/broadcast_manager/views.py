# broadcast_manager/views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from .decorators import role_required, permission_required
from .forms import PublicRegistrationForm, StaffCreationForm
from .models import User, ActivityLog

class CustomLoginView(LoginView):
    template_name = 'broadcast_manager/auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        user = self.request.user
        if user.is_admin():
            return reverse_lazy('broadcast_manager:staff_list')
        elif user.is_producer():
            return reverse_lazy('broadcast_manager:producer_control')
        elif user.is_fcc():
            return reverse_lazy('broadcast_manager:fcc_operations')
        elif user.is_editor():
            return reverse_lazy('broadcast_manager:editor_dashboard')
        return reverse_lazy('broadcast_manager:profile')

def register_public(request):
    if request.user.is_authenticated:
        return redirect('broadcast_manager:profile')
        
    if request.method == 'POST':
        form = PublicRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                'Registration successful! You can now login.'
            )
            return redirect('broadcast_manager:login')
    else:
        form = PublicRegistrationForm()
    
    return render(request, 'broadcast_manager/auth/register.html', {
        'form': form,
        'title': 'Register as Voter/Nominator'
    })

@login_required
@role_required('ADMIN')
def create_staff_account(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.save()
            messages.success(
                request,
                f'Staff account created for {user.username}'
            )
            return redirect('broadcast_manager:staff_list')
    else:
        form = StaffCreationForm()
    
    return render(request, 'broadcast_manager/staff/create.html', {
        'form': form,
        'title': 'Create Staff Account'
    })

@login_required
@role_required('ADMIN')
def staff_list(request):
    staff_members = User.objects.filter(is_staff=True).order_by('username')
    paginator = Paginator(staff_members, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'broadcast_manager/staff/list.html', {
        'page_obj': page_obj,
        'title': 'Staff Members'
    })

@login_required
@role_required('ADMIN', 'EDITOR')
def editor_dashboard(request):
    logs = ActivityLog.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:50]
    
    return render(request, 'broadcast_manager/dashboards/editor.html', {
        'activity_logs': logs,
        'title': 'Editor Dashboard'
    })

@login_required
@role_required('ADMIN', 'PRODUCER')
def producer_control(request):
    logs = ActivityLog.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:50]
    
    return render(request, 'broadcast_manager/dashboards/producer.html', {
        'activity_logs': logs,
        'title': 'Producer Control Panel'
    })

@login_required
@role_required('ADMIN', 'FCC')
def fcc_operations(request):
    logs = ActivityLog.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:50]
    
    return render(request, 'broadcast_manager/dashboards/fcc.html', {
        'activity_logs': logs,
        'title': 'FCC Operations'
    })

@login_required
def profile_view(request):
    return render(request, 'broadcast_manager/profile.html', {
        'user': request.user,
        'title': 'User Profile'
    })

@login_required
@role_required('ADMIN')
def activity_logs(request):
    logs = ActivityLog.objects.all().select_related('user')
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'broadcast_manager/activity/logs.html', {
        'page_obj': page_obj,
        'title': 'Activity Logs'
    })