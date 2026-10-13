import json
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Language, Lesson

class Command(BaseCommand):
    help='Seed the authored low-level progression. Re-running updates content without duplicating lessons.'
    @transaction.atomic
    def handle(self,*args,**options):
        catalog=json.loads((Path(__file__).resolve().parents[2]/'content'/'catalog.json').read_text())
        count=0;active_languages=[];active_lessons=[]
        for order,track in enumerate(catalog,1):
            # Reuse the authored track even if its display name changes.
            language=Language.objects.filter(slug=track['slug']).order_by('pk').first()
            if language is None:
                language=Language.objects.filter(name=track['name']).order_by('pk').first()
            if language is None:language=Language()
            for key in ('name','slug','description','engine','subtitle'):setattr(language,key,track[key])
            language.order=order;language.is_archived=False;language.save()
            active_languages.append(language.pk)
            for lesson_order,l in enumerate(track['lessons'],1):
                defaults={k:v for k,v in l.items() if k!='file'}
                defaults['content']=(Path(__file__).resolve().parents[2]/'content'/'lessons'/l['file']).read_text()
                defaults['challenge']='## '+re.split(r'^## ',defaults['content'],flags=re.M)[-1]
                defaults['is_archived']=False
                lesson,_=Lesson.objects.update_or_create(language=language,order=lesson_order,defaults=defaults)
                active_lessons.append(lesson.pk);count+=1
        # Keep historical rows, completions and drafts; retire stale teaching.
        Language.objects.exclude(pk__in=active_languages).update(is_archived=True)
        Lesson.objects.exclude(pk__in=active_lessons).update(is_archived=True)
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(catalog)} tracks and {count} lessons.'))
