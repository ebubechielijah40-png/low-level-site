from django.contrib import admin
from .models import (Language,Lesson,UserProgress,LessonCompletion,HardwareSystem,
                     HardwareChallenge,HardwareProgress,CodeDraft,BootProject)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display=('name','order','engine','slug')
    ordering=('order',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display=('title','language','order','minutes')
    list_filter=('language',)
    search_fields=('title','content')

@admin.register(HardwareChallenge)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display=('title','system','component','order','language')
    list_filter=('system','language')

admin.site.register([UserProgress,LessonCompletion,HardwareSystem,HardwareProgress,CodeDraft,BootProject])
admin.site.site_header='Bare Metal content administration'
admin.site.site_title='Bare Metal admin'
