# StreamSMS/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def homepage(request):
    return render(request, 'homepage.html')

@login_required
def system_dashboard(request):
    return render(request, 'dashboard.html')  

@login_required
def profile(request):
    user = request.user
    return render(request, 'accounts/profile.html', {'user': user})