from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def homepage(request):
    return render(request, 'homepage.html')

@login_required
def profile(request):
    user = request.user
    return render(request, 'profile.html', {'user': user})