# apps/messages_app/views.py
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.feedgenerator import Rss201rev2Feed
from .models import Message
import datetime
import africastalking

@csrf_exempt
def africastalking_webhook(request):
    if request.method == 'POST':
        from_number = request.POST.get('from')
        message_body = request.POST.get('text')

        Message.objects.create(from_number=from_number, message_body=message_body)

        return HttpResponse("Your message has been received and is pending moderation.")
    return HttpResponse(status=405)

@login_required
def moderation_interface(request):
    messages_list = Message.objects.filter(approved=False, declined=False).order_by('-created_at')
    paginator = Paginator(messages_list, 13)

    page_number = request.GET.get('page')
    messages = paginator.get_page(page_number)
    
    return render(request, 'messages_app/moderation.html', {'messages': messages})

@login_required
def approve_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    message.approved = True
    message.save()
    next_page = request.GET.get('next', 'messages_app:moderation_interface')
    return redirect(next_page)

@login_required
def decline_message(request, id):
    message = get_object_or_404(Message, id=id)
    message.declined = True
    message.save()
    next_page = request.GET.get('next', 'messages_app:moderation_interface')
    return redirect(next_page)

def mask_phone_number(phone_number):
    return f"{phone_number[:5]}** ** {phone_number[-2:]}"

def generate_rss_json(request):
    approved_messages = Message.objects.filter(approved=True)
    items = []

    for message in approved_messages:
        masked_number = mask_phone_number(message.from_number)
        items.append({
            'from': masked_number,
            'message': message.message_body,
            'pubDate': message.created_at.strftime("%a, %d %b %Y %H:%M")
        })
    
    return JsonResponse({
        'version': '2.0',
        'channel': {
            'items': items
        }
    })

def generate_rss(request):
    approved_messages = Message.objects.filter(approved=True)
    feed = Rss201rev2Feed(
        title="Approved Messages",
        link=request.build_absolute_uri('/messages/rss'),
        description="Approved SMS messages",
        language="en",
    )

    for message in approved_messages:
        masked_number = mask_phone_number(message.from_number)
        feed.add_item(
            title=masked_number,
            link=request.build_absolute_uri(f'/messages/{message.id}'),
            description=message.message_body,
            pubdate=message.created_at,
        )
    
    response = HttpResponse(content_type='application/rss+xml')
    feed.write(response, 'utf-8')
    return response

def generate_concatenated_rss_json(request):
    approved_messages = Message.objects.filter(approved=True)
    concatenated_messages = ' | '.join(
        [f"{mask_phone_number(message.from_number)} - {message.message_body}" 
         for message in approved_messages]
    )

    return JsonResponse({
        'version': '2.0',
        'channel': {
            'title': 'Approved Messages Feed',
            'description': concatenated_messages,
        }
    })

@login_required
def messages_list(request):
    messages_list = Message.objects.all().order_by('-created_at')
    paginator = Paginator(messages_list, 13)

    page_number = request.GET.get('page')
    messages = paginator.get_page(page_number)
    
    return render(request, 'messages_app/messages_list.html', {'messages': messages})

@login_required
def message_detail(request, id):
    message = get_object_or_404(Message, id=id)
    return render(request, 'messages_app/message_detail.html', {'message': message})