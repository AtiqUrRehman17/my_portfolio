import json
import urllib.error
import urllib.request
from datetime import date, datetime

from django.core.cache import cache
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile, Skill, Project, Experience, Education
from .forms import ContactForm
from .context_processors import site_profile

GITHUB_CONTRIBUTIONS_CACHE_KEY = 'github_contributions_v1'
GITHUB_CONTRIBUTIONS_CACHE_TTL = 60 * 60 * 6  # 6 hours


def _group_contributions_by_week(days):
    """Reshape a flat, date-ordered list of days into Sunday-Saturday week
    columns, matching GitHub's own contribution graph layout."""
    weeks = []
    current_week = []
    for day in days:
        weekday = (datetime.strptime(day['date'], '%Y-%m-%d').weekday() + 1) % 7  # Sun=0 .. Sat=6
        if weekday == 0 and current_week:
            weeks.append(current_week)
            current_week = []
        while weekday > len(current_week):
            current_week.append(None)
        current_week.append({'date': day['date'], 'count': day.get('count', 0), 'level': day.get('level', 0)})
    if current_week:
        weeks.append(current_week)
    return weeks


def get_github_contributions(profile):
    """Fetch the last year of public GitHub contributions for the profile's
    GitHub username, cached for a few hours. Returns None on any failure
    (network error, unexpected response, no GitHub URL set) so the calling
    template can simply hide the section rather than break the page."""
    if not profile or not profile.github_url:
        return None

    username = profile.github_url.rstrip('/').split('/')[-1]
    if not username:
        return None

    cache_key = f'{GITHUB_CONTRIBUTIONS_CACHE_KEY}:{username}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached or None

    url = f'https://github-contributions-api.jogruber.de/v4/{username}?y=last'
    try:
        with urllib.request.urlopen(url, timeout=4) as response:
            data = json.loads(response.read().decode('utf-8'))
        days = data.get('contributions', [])
        result = {
            'weeks': _group_contributions_by_week(days),
            'total': sum(day.get('count', 0) for day in days),
        }
    except (urllib.error.URLError, TimeoutError, ValueError, OSError, KeyError):
        result = None

    # Cache the outcome either way (including failures) so a down/slow
    # third-party API can't slow down or spam-retry on every page load.
    cache.set(cache_key, result if result else False, GITHUB_CONTRIBUTIONS_CACHE_TTL)
    return result


def home(request):
    # Reuses the same request-cached profile the site_profile context
    # processor already fetches, instead of querying it a second time.
    profile = site_profile(request)['site_profile']
    skills = Skill.objects.all()
    featured_projects = Project.objects.filter(featured=True)[:3]
    experiences = Experience.objects.all()[:3]

    earliest_experience = Experience.objects.order_by('start_date').first()
    if earliest_experience:
        years_experience = max(1, date.today().year - earliest_experience.start_date.year)
    else:
        years_experience = 1

    github_contributions = get_github_contributions(profile)

    context = {
        'skills': skills,
        'featured_projects': featured_projects,
        'experiences': experiences,
        'years_experience': years_experience,
        'projects_count': Project.objects.count(),
        'skills_count': Skill.objects.count(),
        'github_contributions': github_contributions,
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
