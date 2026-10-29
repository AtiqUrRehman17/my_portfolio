from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.utils.text import slugify


class Profile(models.Model):
    name = models.CharField(max_length=120, default='Atiq Ur Rehman')
    professional_title = models.CharField(max_length=180, default='AI/ML & Backend Engineer')
    short_bio = models.CharField(max_length=300, blank=True)
    about = models.TextField(blank=True)
    email = models.EmailField()
    location = models.CharField(max_length=120, blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    profile_image_alt = models.CharField(max_length=180, blank=True)
    resume = models.FileField(
        upload_to='resume/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['pdf'])],
        help_text='Upload a PDF résumé.',
    )
    intro_video = models.FileField(
        upload_to='intro-video/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['mp4', 'webm', 'mov'])],
        help_text='A short intro video (MP4 recommended, H.264). Keep it well compressed — '
                  'aim under ~30MB — since PythonAnywhere free accounts have a 512MB total '
                  'disk quota shared with your database and every uploaded image.',
    )
    intro_video_poster = models.ImageField(
        upload_to='intro-video/',
        blank=True,
        null=True,
        help_text='Optional cover frame shown before the video plays or loads.',
    )
    available_for_work = models.BooleanField(default=True)
    availability_text = models.CharField(max_length=160, default='Open to meaningful opportunities')
    currently_exploring = models.CharField(
        max_length=300,
        blank=True,
        help_text="Comma-separated list of things you're currently building or exploring — "
                  "shown as a rotating line on the home page, e.g. "
                  "'Voice-native RAG systems, Production ML pipelines, Agentic AI workflows'.",
    )

    class Meta:
        verbose_name = 'Site profile'
        verbose_name_plural = 'Site profile'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk and Profile.objects.exists():
            self.pk = Profile.objects.first().pk
        super().save(*args, **kwargs)


class Skill(models.Model):
    SKILL_TYPES = [
        ('ML', 'Machine Learning'),
        ('DL', 'Deep Learning'),
        ('GenAI', 'Generative AI'),
        ('Agentic AI', 'Agentic AI'),
        ('Deployment', 'Deployment AWS'),
        ('Containerization', 'Containerization Docker'),
        ('BE', 'Backend'),
        ('fastapi', 'FastAPI'),
        ('DB', 'Databases'),
        ('Django', 'Django'),
        ('TOOL', 'Tools & Technologies'),
        ('LANG', 'Programming Languages'),
    ]
    
    name = models.CharField(max_length=100)
    skill_type = models.CharField(max_length=20, choices=SKILL_TYPES)
    proficiency = models.IntegerField(help_text="Proficiency percentage (0-100)")
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    description = models.CharField(max_length=240, blank=True, help_text="Briefly describe how you use this technology.")
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class Project(models.Model):
    CATEGORY_CHOICES = [
        ('ai-ml', 'AI & Machine Learning'),
        ('generative-ai', 'Generative AI'),
        ('backend', 'Backend Engineering'),
        ('full-stack', 'Full Stack'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    short_summary = models.CharField(
        max_length=240,
        blank=True,
        help_text="A concise summary used on project cards.",
    )
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    technologies = models.CharField(max_length=500, help_text="Comma-separated technologies used")
    github_link = models.URLField(blank=True)
    live_link = models.URLField(blank=True)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    image_alt = models.CharField(max_length=180, blank=True, help_text="Describe the cover image for accessibility.")
    featured = models.BooleanField(default=False)
    created_date = models.DateField(default=timezone.now)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first within the same group.")

    # Structured case-study content
    role = models.CharField(max_length=200, blank=True)
    problem = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    architecture = models.TextField(blank=True)
    key_features = models.TextField(blank=True, help_text="Enter one feature per line.")
    challenges = models.TextField(blank=True)
    results = models.TextField(blank=True)
    pipeline_steps = models.CharField(
        max_length=400,
        blank=True,
        help_text="Comma-separated pipeline stages for an animated architecture diagram on "
                  "the case study page, e.g. 'Upload, Deepgram STT, LangChain Retrieval, "
                  "GPT-4o mini, ElevenLabs TTS'. Leave blank to hide the diagram.",
    )

    class Meta:
        ordering = ['-featured', 'order', '-created_date']
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'project'
            candidate = base_slug
            suffix = 2
            while Project.objects.exclude(pk=self.pk).filter(slug=candidate).exists():
                candidate = f'{base_slug}-{suffix}'
                suffix += 1
            self.slug = candidate
        super().save(*args, **kwargs)
    
    def get_tech_list(self):
        return [tech.strip() for tech in self.technologies.split(',')]

    def get_feature_list(self):
        return [feature.strip() for feature in self.key_features.splitlines() if feature.strip()]

    def get_pipeline_steps(self):
        return [step.strip() for step in self.pipeline_steps.split(',') if step.strip()]

    @property
    def card_summary(self):
        return self.short_summary or self.description


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='projects/gallery/')
    caption = models.CharField(max_length=240, blank=True)
    alt_text = models.CharField(max_length=180, help_text="Describe the image for visitors using screen readers.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.project.title} image {self.order + 1}'

class Experience(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    description = models.TextField()
    achievements = models.TextField(blank=True, help_text="Enter one achievement per line.")
    technologies = models.CharField(max_length=500, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.title} at {self.company}"

    def get_tech_list(self):
        return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]

    def get_achievement_list(self):
        return [item.strip() for item in self.achievements.splitlines() if item.strip()]

class Education(models.Model):
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year = models.CharField(max_length=20)
    grade = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-year']
    
    def __str__(self):
        return f"{self.degree} - {self.institution}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
