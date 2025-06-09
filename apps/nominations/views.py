# apps/nominations/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Count
from .models import MainCategory, NominationCategory, Nominee, Vote
from .forms import NomineeForm, VoteForm

@csrf_exempt
def ussd_handler(request):
    if request.method == 'POST':
        session_id = request.POST.get('sessionId')
        phone_number = request.POST.get('phoneNumber')
        text = request.POST.get('text', '').strip()

        response = "CON Welcome to Awards Nominations\n"
        
        if not text:
            response += "1. View Categories\n2. Vote"
        elif text == '1':
            categories = MainCategory.objects.all()
            response = "CON Select Category:\n" + "\n".join(
                f"{i}. {cat.name}" for i, cat in enumerate(categories, 1)
            )
        elif text.startswith('1.'):
            parts = text.split('.')
            if len(parts) == 2:
                try:
                    category = MainCategory.objects.all()[int(parts[1])-1]
                    subcategories = category.subcategories.all()
                    response = f"CON {category.name} Subcategories:\n" + "\n".join(
                        f"{i}. {sub.name}" for i, sub in enumerate(subcategories, 1)
                    )
                except IndexError:
                    response = "END Invalid selection"
        elif text == '2':
            nominees = Nominee.objects.filter(approved=True).select_related('category')
            response = "CON Select Nominee:\n" + "\n".join(
                f"{i}. {nom.name} ({nom.category.name})" 
                for i, nom in enumerate(nominees, 1)
            )
        elif text.startswith('2.'):
            try:
                nominee = Nominee.objects.filter(approved=True)[int(text.split('.')[1])-1]
                Vote.objects.create(
                    nominee=nominee,
                    voter_identifier=phone_number,
                    voter_type='ussd'
                )
                response = f"END Thank you for voting for {nominee.name}!"
            except (IndexError, ValueError):
                response = "END Invalid selection"

        return HttpResponse(response, content_type='text/plain')

def category_detail(request, slug):
    category = get_object_or_404(MainCategory, slug=slug)
    subcategories = category.subcategories.annotate(
        nominee_count=Count('nominees'),
        approved_nominees=Count('nominees', filter=models.Q(nominees__approved=True)))
    return render(request, 'nominations/category_detail.html', {
        'category': category,
        'subcategories': subcategories
    })

def nominate(request):
    if request.method == 'POST':
        form = NomineeForm(request.POST)
        if form.is_valid():
            nominee = form.save(commit=False)
            nominee.approved = False
            nominee.save()
            messages.success(request, 'Nomination submitted for approval!')
            return redirect('nominations:success')
    else:
        form = NomineeForm()
    
    return render(request, 'nominations/nominate.html', {
        'form': form,
        'categories': NominationCategory.objects.all()
    })

def vote(request):
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vote recorded successfully!')
            return redirect('nominations:success')
    else:
        form = VoteForm()
    
    nominees = Nominee.objects.filter(approved=True).select_related('category')
    return render(request, 'nominations/vote.html', {
        'form': form,
        'nominees': nominees
    })