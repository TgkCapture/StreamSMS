from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MainCategory, NominationCategory, Nominee, Vote
from .forms import NomineeForm, VoteForm

@csrf_exempt 
def ussd_handler(request):
    if request.method == 'POST':
        session_id = request.POST.get('sessionId')
        service_code = request.POST.get('serviceCode')
        phone_number = request.POST.get('phoneNumber')
        text = request.POST.get('text')

        # USSD flow Logic
        response_text = ""
        if text == "":
            response_text = "CON Welcome to the Awards Nomination.\n"
            response_text += "1. Nominations\n"
            response_text += "2. Vote\n"
        elif text == "1":
            categories = MainCategory.objects.all()
            response_text = "CON Choose a category:\n"
            for index, category in enumerate(categories, start=1):
                response_text += f"{index}. {category.name}\n"
        elif text.startswith("1."):
            category_index = int(text.split('.')[0]) - 1
            category = MainCategory.objects.all()[category_index]
            nominations = NominationCategory.objects.filter(main_category=category)
            response_text = f"CON Nominations for {category.name}:\n"
            for index, nomination in enumerate(nominations, start=1):
                response_text += f"{index}. {nomination.name}\n"
        elif text.startswith("2."):
            # Display approved nominees for voting
            nominees = Nominee.objects.filter(approved=True)
            response_text = "CON Choose a nominee to vote for:\n"
            for index, nominee in enumerate(nominees, start=1):
                response_text += f"{index}. {nominee.name}\n"
        elif text.startswith("2."):
            nominee_index = int(text.split('.')[0]) - 1
            nominees = Nominee.objects.filter(approved=True)
            if nominee_index < len(nominees):
                nominee = nominees[nominee_index]
                # Save the vote
                Vote.objects.get_or_create(
                    nominee=nominee,
                    voter_identifier=phone_number,
                    voter_type='ussd'
                )
                response_text = f"END Thank you for voting for {nominee.name}!"
            else:
                response_text = "END Invalid nominee selection."

        return HttpResponse(response_text, content_type='text/plain')
        return HttpResponse(response_text, content_type='text/plain')

def nominate(request):
    if request.method == 'POST':
        form = NomineeForm(request.POST)
        if form.is_valid():
            nominee = form.save(commit=False)
            nominee.approved = False
            nominee.save()
            return redirect('nomination_success')
    else:
        form = NomineeForm()
    
    return render(request, 'nominations/nominate.html', {'form': form})

def vote(request):
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vote_success')
    else:
        form = VoteForm()
    
    nominees = Nominee.objects.filter(approved=True)
    return render(request, 'nominations/vote.html', {'form': form, 'nominees': nominees})