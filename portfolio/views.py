from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile, Skill, Project, Experience, Education
from .forms import ContactForm

def home(request):
    profile = Profile.objects.first()
    skills = Skill.objects.all()
    featured_projects = Project.objects.filter(featured=True)[:3]
    experiences = Experience.objects.all()[:3]
    
    context = {
        'skills': skills,
        'featured_projects': featured_projects,
        'experiences': experiences,
        'profile': profile,
    }
    return render(request, 'portfolio/home.html', context)

def projects(request):
    projects_list = Project.objects.all()
    categories = [
        {'value': value, 'label': label}
        for value, label in Project.CATEGORY_CHOICES
        if projects_list.filter(category=value).exists()
    ]
    return render(request, 'portfolio/projects.html', {
        'projects': projects_list,
        'categories': categories,
    })

def project_detail(request, slug):
    project = get_object_or_404(Project.objects.prefetch_related('gallery_images'), slug=slug)
    return render(request, 'portfolio/project_detail.html', {'project': project})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            
            # Send email notification
            try:
                send_mail(
                    f"Portfolio Contact: {contact_message.subject}",
                    f"From: {contact_message.name}\nEmail: {contact_message.email}\n\nMessage:\n{contact_message.message}",
                    settings.EMAIL_HOST_USER,
                    [settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
                messages.success(request, 'Thank you for your message! I will get back to you soon.')
            except Exception as e:
                messages.warning(request, 'Your message was saved, but email notification failed. I will still see your message.')
            
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'portfolio/contact.html', {'form': form})

def resume(request):
    experiences = Experience.objects.all()
    education = Education.objects.all()
    skills = Skill.objects.all()
    
    context = {
        'experiences': experiences,
        'education': education,
        'skills': skills,
    }
    return render(request, 'portfolio/resume.html', context)
