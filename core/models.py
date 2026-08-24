from django.db import models
from django.contrib.auth.models import User


class Language(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Lesson(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.IntegerField(default=0)
    challenge = models.TextField()
    starter_code = models.TextField(default='')
    example_output = models.TextField(default='')

    class Meta:
        ordering = ['order']
        unique_together = ('language', 'order')

    def __str__(self):
        return f"{self.language.name} - [{self.order}] {self.title}"


class LessonCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_lessons')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')


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
    starter_code_asm_x86 = models.TextField(default='')
    starter_code_asm_arm = models.TextField(default='')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']


class HardwareProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(HardwareChallenge, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    language_used = models.CharField(max_length=50, default='c')

    class Meta:
        unique_together = ('user', 'challenge')
