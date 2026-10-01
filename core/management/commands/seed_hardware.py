import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Language, HardwareSystem, HardwareChallenge

class Command(BaseCommand):
    help='Upgrade the original six systems into open, testable component configuration labs.'
    @transaction.atomic
    def handle(self,*args,**options):
        root=Path(__file__).resolve().parents[2]/'content';systems=json.loads((root/'hardware.json').read_text())
        count=0
        for order,s in enumerate(systems,1):
            system,_=HardwareSystem.objects.update_or_create(slug=s['slug'],defaults={k:s[k] for k in ('name','category','description')}|{'unlock_order':order})
            for index,l in enumerate(s['labs'],1):
                language=Language.objects.filter(slug=l['language_slug']).first()
                defaults={k:l[k] for k in ('title','description','component','starter_code_c','starter_code_asm','expected_state')}
                defaults['instructions']=(root/'lessons'/l['file']).read_text();defaults['language']=language
                HardwareChallenge.objects.update_or_create(system=system,order=index,defaults=defaults);count+=1
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(systems)} component models and {count} configuration labs.'))
