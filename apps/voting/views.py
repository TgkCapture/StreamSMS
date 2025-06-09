# apps/voting/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import VoteSession, Vote
from .forms import VoteForm
from apps.nominations.models import Nominee

@require_http_methods(["GET", "POST"])
@login_required
def vote(request):
    session = VoteSession.objects.filter(
        is_active=True,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).first()

    if not session:
        messages.info(request, "There is currently no active voting session.")
        return render(request, 'voting/no_active_session.html')

    # Check if user has already voted
    if Vote.objects.filter(session=session, user=request.user).exists():
        messages.warning(request, "You have already voted in this session.")
        return redirect('voting:results')

    if request.method == 'POST':
        form = VoteForm(request.POST, session=session)
        if form.is_valid():
            Vote.objects.create(
                nominee=form.cleaned_data['nominee'],
                session=session,
                user=request.user,
                voter_identifier=request.user.username,
                voter_type='web',
                ip_address=get_client_ip(request)
            )
            messages.success(request, "Your vote has been recorded successfully!")
            return redirect('voting:results')
    else:
        form = VoteForm(session=session)

    return render(request, 'voting/vote.html', {
        'form': form,
        'session': session
    })

@require_http_methods(["GET"])
def ussd_vote(request):
    session = VoteSession.objects.filter(
        is_active=True,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).first()

    if not session:
        return JsonResponse({"message": "END Voting is not currently active"})

    phone_number = request.GET.get("phoneNumber", "")
    text = request.GET.get("text", "").strip()

    if not text:
        nominees = Nominee.objects.filter(approved=True).order_by('name')
        response = "CON Choose a nominee:\n" + "\n".join(
            f"{i}. {nom.name}" for i, nom in enumerate(nominees, 1)
        )
        return JsonResponse({"message": response})

    try:
        choice = int(text) - 1
        nominee = Nominee.objects.filter(approved=True).order_by('name')[choice]
        
        # Check if phone number has already voted
        if Vote.objects.filter(session=session, voter_identifier=phone_number).exists():
            return JsonResponse({"message": "END You have already voted in this session"})

        Vote.objects.create(
            nominee=nominee,
            session=session,
            voter_identifier=phone_number,
            voter_type='ussd',
            ip_address=get_client_ip(request)
        )
        return JsonResponse({"message": f"END Thank you for voting for {nominee.name}!"})
    except (IndexError, ValueError):
        return JsonResponse({"message": "END Invalid selection. Please try again."})

@require_http_methods(["GET"])
def results(request):
    session = VoteSession.objects.filter(
        is_active=True,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).first()

    if not session:
        return render(request, 'voting/no_active_session.html')

    nominees = Nominee.objects.filter(
        voting_votes__session=session
    ).annotate(
        total_votes=Count('voting_votes')
    ).order_by('-total_votes')

    return render(request, 'voting/results.html', {
        'session': session,
        'nominees': nominees
    })

@require_http_methods(["GET"])
def results_api(request):
    session = VoteSession.objects.filter(
        is_active=True,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).first()

    if not session:
        return JsonResponse({'error': 'No active session'}, status=400)

    nominees = Nominee.objects.filter(
        voting_votes__session=session
    ).annotate(
        votes=Count('voting_votes')
    ).order_by('-votes').values('name', 'votes')

    return JsonResponse({
        'session': session.name,
        'results': list(nominees)
    })

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')