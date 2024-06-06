from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message
import datetime

@csrf_exempt
def sms_webhook(request):
    if request.method == 'POST':
        from_number = request.POST.get('From')
        message_body = request.POST.get('Body')
        Message.objects.create(from_number=from_number, message_body=message_body, approved=False)
        return HttpResponse("Message received", status=200)
    return HttpResponse(status=405)

def moderation_interface(request):
    messages = Message.objects.filter(approved=False)
    return render(request, 'messages/moderation.html', {'messages': messages})

def approve_message(request, message_id):
    message = Message.objects.get(id=message_id)
    message.approved = True
    message.save()
    return redirect('moderation_interface')