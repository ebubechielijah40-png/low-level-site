from django.contrib import admin
from .models import Language, Lesson, LessonCompletion, HardwareSystem, HardwareChallenge, HardwareProgress

admin.site.register(Language)
admin.site.register(Lesson)
admin.site.register(LessonCompletion)
admin.site.register(HardwareSystem)
admin.site.register(HardwareChallenge)
admin.site.register(HardwareProgress)
