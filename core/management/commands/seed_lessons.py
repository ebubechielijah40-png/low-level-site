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
        count=0
        for order,track in enumerate(catalog,1):
            language,_=Language.objects.update_or_create(name=track['name'],defaults={k:track[k] for k in ('slug','description','engine','subtitle')}|{'order':order})
            for lesson_order,l in enumerate(track['lessons'],1):
                defaults={k:v for k,v in l.items() if k!='file'}
                defaults['content']=(Path(__file__).resolve().parents[2]/'content'/'lessons'/l['file']).read_text()
                defaults['challenge']=re.split(r'^## ',defaults['content'],flags=re.M)[-1]
                Lesson.objects.update_or_create(language=language,order=lesson_order,defaults=defaults);count+=1
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(catalog)} tracks and {count} lessons.'))
