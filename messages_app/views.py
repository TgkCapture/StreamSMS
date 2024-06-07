from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
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

def decline_message(request, id):
    message = get_object_or_404(Message, id=id)
    message.delete()
    return redirect('moderation_interface')

def generate_rss(request):
    approved_messages = Message.objects.filter(approved=True)
    items = []

    for message in approved_messages:
        items.append({
            'sender': message.from_number,
            'message': message.message_body,
            'link': f"http://127.0.0.1:8000/messages/{message.id}",
            # 'pubDate': datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        })
    
    rss_feed_json = {
        'version': '2.0',
        'channel': {
            'title': 'Approved Messages',
            'link': 'http://127.0.0.1:8000/messages/rss',
            'description': 'Approved SMS messages',
            'items': items
        }
    }
    
    return JsonResponse(rss_feed_json)

def messages_list(request):
    messages = Message.objects.all()
    return render(request, 'messages/messages_list.html', {'messages': messages})

def message_detail(request, id):
    message = get_object_or_404(Message, id=id)
    return render(request, 'messages/message_detail.html', {'message': message})