from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import VoteSession, Vote
from nominations.models import Nominee
from .forms import VoteForm
from django.utils import timezone
from django.http import JsonResponse

def vote(request):
    # Fetch the active voting session
    session = VoteSession.objects.filter(active=True, start_time__lte=timezone.now(), end_time__gte=timezone.now()).first()
    
    if not session:
        messages.info(request, "There is currently no active voting session.")
        return redirect('homepage')
    
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            nominee = form.cleaned_data['nominee']
            
            # Create a new vote record
            Vote.objects.create(
                nominee=nominee,
                session=session,
                user=request.user if request.user.is_authenticated else None,
                voter_identifier=str(request.user.id) if request.user.is_authenticated else "anonymous_web",
                voter_type="web"
            )
            messages.success(request, "Your vote has been cast successfully!")
            return redirect('results') 
    else:
        form = VoteForm()
    
    nominees = Nominee.objects.all()
    return render(request, 'voting/vote.html', {'form': form, 'nominees': nominees})

def ussd_vote(request):
    session_id = request.GET.get("sessionId")
    service_code = request.GET.get("serviceCode")
    phone_number = request.GET.get("phoneNumber")
    text = request.GET.get("text", "")
    
    session = VoteSession.objects.filter(active=True, start_time__lte=timezone.now(), end_time__gte=timezone.now()).first()
    
    if not session:
        return JsonResponse({"message": "END Voting is not currently active."})

    if text == "":
        response = "CON Choose a nominee:\n"
        for idx, nominee in enumerate(Nominee.objects.all(), start=1):
            response += f"{idx}. {nominee.name}\n"
        return JsonResponse({"message": response})
    
    try:
        choice = int(text.strip()) - 1
        nominee = Nominee.objects.all()[choice]
        
        # Create a new vote record
        Vote.objects.create(
            nominee=nominee,
            session=session,
            voter_identifier=phone_number,
            voter_type="ussd"
        )
        return JsonResponse({"message": "END Thank you! Your vote has been recorded."})
    except (IndexError, ValueError):
        return JsonResponse({"message": "END Invalid choice. Please try again."})

def results(request):
    # Fetch all nominees with their vote counts in the active session
    session = VoteSession.objects.filter(active=True, start_time__lte=timezone.now(), end_time__gte=timezone.now()).first()
    if not session:
        messages.info(request, "No active voting session to show results for.")
        return redirect('homepage')
    
    nominees = Nominee.objects.filter(vote__session=session).annotate(total_votes=Count('vote')).order_by('-total_votes')
    
    return render(request, 'voting/results.html', {'nominees': nominees})        