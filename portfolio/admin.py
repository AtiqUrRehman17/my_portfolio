from django.contrib import admin
from .models import Profile, Skill, Project, ProjectImage, Experience, Education, ContactMessage


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Identity', {'fields': ('name', 'professional_title', 'short_bio', 'about')}),
        ('Contact', {'fields': ('email', 'location', 'github_url', 'linkedin_url')}),
        ('Media', {'fields': ('profile_image', 'profile_image_alt', 'resume')}),
        ('Intro video', {'fields': ('intro_video', 'intro_video_poster')}),
        ('Availability', {'fields': ('available_for_work', 'availability_text', 'currently_exploring')}),
    ]

    def has_add_permission(self, request):
        return not Profile.objects.exists()

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'skill_type', 'order']
    list_filter = ['skill_type']
    search_fields = ['name']

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'alt_text', 'caption', 'order']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'featured', 'order', 'created_date']
    list_editable = ['featured', 'order']
    list_filter = ['category', 'featured', 'created_date']
    search_fields = ['title', 'short_summary', 'description', 'technologies']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectImageInline]
    fieldsets = [
        ('Project identity', {'fields': ('title', 'slug', 'short_summary', 'category', 'role')}),
        ('Overview', {'fields': ('description', 'technologies')}),
        ('Case study', {'fields': ('problem', 'solution', 'architecture', 'pipeline_steps', 'key_features', 'challenges', 'results')}),
        ('Links', {'fields': ('github_link', 'live_link')}),
        ('Cover image', {'fields': ('image', 'image_alt')}),
        ('Publishing', {'fields': ('featured', 'order', 'created_date')}),
    ]

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'start_date', 'end_date', 'current']
    list_filter = ['current', 'company']
    search_fields = ['title', 'company', 'description']
    fieldsets = [
        ('Role', {'fields': ('title', 'company', 'location', 'start_date', 'end_date', 'current')}),
        ('Impact', {'fields': ('description', 'achievements')}),
        ('Technology and ordering', {'fields': ('technologies', 'order')}),
    ]

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'institution', 'year']
    search_fields = ['degree', 'institution']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_date', 'is_read']
    list_editable = ['is_read']
    list_filter = ['is_read', 'created_date']
    search_fields = ['name', 'email', 'subject', 'message']
    actions = ['mark_as_read', 'mark_as_unread']

    @admin.action(description='Mark selected messages as read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description='Mark selected messages as unread')
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
