from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Language(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(default='', blank=True)
    order = models.PositiveIntegerField(default=0)
    engine = models.CharField(max_length=20, default='c')
    subtitle = models.CharField(max_length=180, default='', blank=True)

    class Meta:
        ordering = ['order', 'pk']

    def __str__(self):
        return self.name


class Lesson(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField()
    challenge = models.TextField()
    starter_code = models.TextField(default='')
    example_output = models.TextField(default='')
    summary = models.CharField(max_length=240, default='', blank=True)
    expected_state = models.JSONField(default=dict, blank=True)
    minutes = models.PositiveIntegerField(default=25)

    class Meta:
        ordering = ['order']
        unique_together = ['language', 'order']

    def __str__(self):
        return f"{self.language.name} — {self.order}. {self.title}"


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    current_lesson = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'language']

    def __str__(self):
        return f"{self.user.username} progress in {self.language.name}: {self.current_lesson}"


class HardwareSystem(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50)
    unlock_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class HardwareChallenge(models.Model):
    system = models.ForeignKey(HardwareSystem, on_delete=models.CASCADE, related_name='challenges')
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField()
    starter_code_c = models.TextField(default='')
    starter_code_asm = models.TextField(default='')
    order = models.IntegerField(default=0)
    component = models.CharField(max_length=50, default='cpu')
    language = models.ForeignKey(Language, null=True, blank=True, on_delete=models.SET_NULL, related_name='configurations')
    expected_state = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.system.name} — {self.title}"


class HardwareProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(HardwareChallenge, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    language_used = models.CharField(max_length=50, default='c')

    class Meta:
        unique_together = ('user', 'challenge')

    def __str__(self):
        return f"{self.user.username} — {self.challenge.title}"


class LessonCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'lesson'], name='one_lesson_completion')]


class CodeDraft(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    code = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'key'], name='one_code_draft')]


class BootProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boot_projects')
    name = models.CharField(max_length=80)
    source = models.TextField(blank=True)
    image_hex = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-updated_at']
