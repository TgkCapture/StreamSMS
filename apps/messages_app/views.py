# apps/messages_app/views.py
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.utils import timezone
from django.utils.feedgenerator import Rss201rev2Feed
from django.db.models import Count, Q
from .models import Message
from django.contrib import messages as django_messages
import africastalking
from datetime import timedelta

# Constants
MESSAGES_PER_PAGE = 13
PHONE_MASK_FORMAT = "{}{}{}** ** {}{}"  # First 3 visible, then mask, last 2 visible

@login_required
def messages_home(request):
    """Dashboard view with message statistics"""
    stats = {
        'total_messages': Message.objects.count(),
        'pending_messages': Message.objects.filter(approved=False, declined=False).count(),
        'approved_messages': Message.objects.filter(approved=True).count(),
        'declined_messages': Message.objects.filter(declined=True).count(),
    }
  
    recent_messages = Message.objects.filter(approved=True).order_by('-created_at')[:5]
    
    return render(request, 'messages_app/home.html', {
        'stats': stats,
        'recent_messages': recent_messages
    })
@csrf_exempt
def africastalking_webhook(request):
    """Webhook for Africa's Talking SMS API"""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    try:
        from_number = request.POST.get('from', '').strip()
        message_body = request.POST.get('text', '').strip()
        
        if not from_number or not message_body:
            return HttpResponse("Invalid message data", status=400)
            
        Message.objects.create(
            from_number=from_number,
            message_body=message_body,
            source='sms'
        )
        
        return HttpResponse("Message received and pending moderation", status=201)
    
    except Exception as e:
        return HttpResponse(f"Error processing message: {str(e)}", status=500)

@login_required
def moderation_interface(request):
    """View for moderating pending messages"""
    query = request.GET.get('q', '')
    messages_list = Message.objects.filter(
        approved=False, 
        declined=False
    ).order_by('-created_at')
    
    if query:
        messages_list = messages_list.filter(
            Q(message_body__icontains=query) |
            Q(from_number__icontains=query)
        )
    
    paginator = Paginator(messages_list, MESSAGES_PER_PAGE)
    page_number = request.GET.get('page')
    
    try:
        messages = paginator.page(page_number)
    except PageNotAnInteger:
        messages = paginator.page(1)
    except EmptyPage:
        messages = paginator.page(paginator.num_pages)
    
    return render(request, 'messages_app/moderation.html', {
        'messages': messages,
        'search_query': query
    })

@login_required
def approve_message(request, message_id):
    """Approve a specific message"""
    message = get_object_or_404(Message, id=message_id)
    
    if not message.approved and not message.declined:
        message.approved = True
        message.moderated_by = request.user
        message.moderated_at = timezone.now()
        message.save()
        django_messages.success(request, "Message approved successfully")
    else:
        django_messages.warning(request, "Message was already moderated")
    
    next_page = request.GET.get('next', 'messages_app:moderation_interface')
    return redirect(next_page)

@login_required
def decline_message(request, message_id):
    """Decline a specific message"""
    message = get_object_or_404(Message, id=message_id)
    
    if not message.approved and not message.declined:
        message.declined = True
        message.moderated_by = request.user
        message.moderated_at = timezone.now()
        message.save()
        django_messages.success(request, "Message declined successfully")
    else:
        django_messages.warning(request, "Message was already moderated")
    
    next_page = request.GET.get('next', 'messages_app:moderation_interface')
    return redirect(next_page)

def mask_phone_number(phone_number):
    """Mask phone number for privacy"""
    if len(phone_number) < 6:
        return phone_number  # Don't mask very short numbers
    
    return PHONE_MASK_FORMAT.format(
        phone_number[0],
        phone_number[1],
        phone_number[2],
        phone_number[-2],
        phone_number[-1]
    )

def generate_rss_json(request):
    """Generate JSON feed of approved messages"""
    approved_messages = Message.objects.filter(approved=True).order_by('-created_at')[:50]
    
    items = [{
        'from': mask_phone_number(msg.from_number),
        'message': msg.message_body,
        'pubDate': msg.created_at.strftime("%a, %d %b %Y %H:%M"),
        'id': msg.id
    } for msg in approved_messages]
    
    return JsonResponse({
        'version': '2.0',
        'channel': {
            'title': 'Approved Messages Feed',
            'items': items,
            'count': len(items)
        }
    }, json_dumps_params={'indent': 2})

def generate_rss(request):
    """Generate RSS feed of approved messages"""
    approved_messages = Message.objects.filter(approved=True).order_by('-created_at')[:50]
    
    feed = Rss201rev2Feed(
        title="Approved Messages Feed",
        link=request.build_absolute_uri('/messages/rss'),
        description="Latest approved SMS messages",
        language="en",
    )

    for message in approved_messages:
        feed.add_item(
            title=f"Message from {mask_phone_number(message.from_number)}",
            link=request.build_absolute_uri(f'/messages/{message.id}'),
            description=message.message_body,
            pubdate=message.created_at,
            author_name=mask_phone_number(message.from_number),
            unique_id=str(message.id),
        )
    
    response = HttpResponse(content_type='application/rss+xml; charset=utf-8')
    feed.write(response, 'utf-8')
    return response

def generate_concatenated_rss_json(request):
    """Generate a single JSON object with all approved messages concatenated"""
    approved_messages = Message.objects.filter(approved=True).order_by('-created_at')
    concatenated = ' | '.join(
        f"{mask_phone_number(msg.from_number)}: {msg.message_body}"
        for msg in approved_messages
    )
    
    return JsonResponse({
        'title': 'Combined Messages Feed',
        'content': concatenated,
        'count': approved_messages.count(),
        'generated_at': timezone.now().isoformat()
    })

@login_required
def messages_list(request):
    """View all messages with filtering options"""
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '')
  
    messages_list = Message.objects.all().order_by('-created_at')

    if status_filter == 'pending':
        messages_list = messages_list.filter(approved=False, declined=False)
    elif status_filter == 'approved':
        messages_list = messages_list.filter(approved=True)
    elif status_filter == 'declined':
        messages_list = messages_list.filter(declined=True)
 
    if search_query:
        messages_list = messages_list.filter(
            Q(message_body__icontains=search_query) |
            Q(from_number__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(messages_list, MESSAGES_PER_PAGE)
    page_number = request.GET.get('page')
    
    try:
        messages = paginator.page(page_number)
    except PageNotAnInteger:
        messages = paginator.page(1)
    except EmptyPage:
        messages = paginator.page(paginator.num_pages)
    
    return render(request, 'messages_app/messages_list.html', {
        'messages_list': messages,
        'status_filter': status_filter,
        'search_query': search_query
    })

@login_required
def message_detail(request, message_id):
    """Detailed view of a single message"""
    message = get_object_or_404(Message, id=message_id)
    
    if (message.approved or message.declined) and not message.moderated_by:
        message.moderated_by = request.user
        message.moderated_at = timezone.now()
        message.save()
    
    return render(request, 'messages_app/message_detail.html', {
        'message': message,
        'masked_number': mask_phone_number(message.from_number)
    })

@login_required
def bulk_action(request):
    """Handle bulk approve/decline actions"""
    if request.method == 'POST':
        action = request.POST.get('action')
        message_ids = request.POST.getlist('message_ids')
        
        if not message_ids:
            django_messages.error(request, "No messages selected")
            return redirect('messages_app:moderation_interface')
        
        messages = Message.objects.filter(
            id__in=message_ids,
            approved=False,
            declined=False
        )
        
        if action == 'approve':
            messages.update(
                approved=True,
                moderated_by=request.user,
                moderated_at=timezone.now()
            )
            django_messages.success(request, f"Approved {messages.count()} messages")
        elif action == 'decline':
            messages.update(
                declined=True,
                moderated_by=request.user,
                moderated_at=timezone.now()
            )
            django_messages.success(request, f"Declined {messages.count()} messages")
        else:
            django_messages.error(request, "Invalid action")
        
    return redirect('messages_app:moderation_interface')

@login_required
def toggle_message_status(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            message.approve(request.user)
            django_messages.success(request, "Message approved successfully")
        elif action == 'decline':
            message.decline(request.user)
            django_messages.success(request, "Message declined successfully")
        elif action == 'reset':
            message.reset_status()
            django_messages.success(request, "Message status reset to pending")
        
        return redirect(request.POST.get('next', 'messages_app:messages_list'))
    
    return redirect('messages_app:message_detail', message_id=message_id)