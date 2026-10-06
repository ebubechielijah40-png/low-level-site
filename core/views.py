import hashlib
import json
import re
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import IntegrityError
from django.db.models import Count, Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .forms import LoginForm, RegisterForm
from .models import (Language, Lesson, UserProgress, LessonCompletion, HardwareSystem,
                     HardwareChallenge, HardwareProgress, CodeDraft, BootProject)
from .code_runner import execute, ENGINES
from .runtime.boot_vm import DEFAULT_BOOT, BootVM, build_boot
from .runtime.common import RunError


def landing(request):
    return render(request,'core/landing.html',{'languages':Language.objects.annotate(lesson_count=Count('lessons'))})

def login_view(request):
    if request.user.is_authenticated:return redirect('dashboard')
    form=LoginForm(request,data=request.POST or None)
    if request.method=='POST' and form.is_valid():
        login(request,form.get_user())
        next_url=request.POST.get('next','')
        if url_has_allowed_host_and_scheme(next_url,{request.get_host()},require_https=request.is_secure()):return redirect(next_url)
        return redirect('dashboard')
    return render(request,'core/login.html',{'form':form,'next':request.GET.get('next','')})

def register(request):
    if request.user.is_authenticated:return redirect('dashboard')
    form=RegisterForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        try:user=User.objects.create_user(form.cleaned_data['username'],form.cleaned_data['email'],form.cleaned_data['password'])
        except IntegrityError:form.add_error('username','This username is already taken.')
        else:
            login(request,user);messages.success(request,'Workspace created. Every lesson and lab is open.');return redirect('dashboard')
    return render(request,'core/register.html',{'form':form})

@login_required
@require_POST
def logout_view(request):
    logout(request);return redirect('landing')

def track_context(user):
    done=set(LessonCompletion.objects.filter(user=user).values_list('lesson_id',flat=True))
    tracks=list(Language.objects.prefetch_related(Prefetch('lessons',
        queryset=Lesson.objects.only('id','language_id','order','title','summary'))))
    for t in tracks:
        ls=list(t.lessons.all());t.lesson_count=len(ls);t.completed=sum(l.pk in done for l in ls)
        t.percentage=round(t.completed/max(1,len(ls))*100)
        t.next_lesson=next((l for l in ls if l.pk not in done),ls[0] if ls else None)
    return tracks,done

@login_required
def dashboard(request):
    tracks,done=track_context(request.user)
    next_lesson=next((t.next_lesson for t in tracks if t.completed<t.lesson_count),None)
    return render(request,'core/dashboard.html',{'tracks':tracks,'done_count':len(done),'total_count':sum(t.lesson_count for t in tracks),
            'next_lesson':next_lesson,'systems':HardwareSystem.objects.annotate(lab_count=Count('challenges')),
            'lab_count':HardwareProgress.objects.filter(user=request.user,completed=True).count(),
            'projects':request.user.boot_projects.all()[:3],'active_nav':'dashboard'})

@login_required
def language_list(request):
    tracks,_=track_context(request.user)
    return render(request,'core/language_list.html',{'tracks':tracks,'active_nav':'languages'})

@login_required
def language_detail(request,pk):
    language=get_object_or_404(Language,pk=pk)
    completed_ids=set(LessonCompletion.objects.filter(user=request.user,lesson__language=language).values_list('lesson_id',flat=True))
    return render(request,'core/language_detail.html',{'language':language,'lessons':language.lessons.only('id','language_id','title','order','summary','minutes'),
            'completed_ids':completed_ids,'configurations':language.configurations.select_related('system').all(),'active_nav':'languages'})

@login_required
def lesson_detail(request,pk=None,language_pk=None,lesson_order=None):
    lesson=get_object_or_404(Lesson.objects.select_related('language'),pk=pk) if pk else get_object_or_404(Lesson,language_id=language_pk,order=lesson_order)
    lessons=list(lesson.language.lessons.only('id','language_id','title','order'));key=f'lesson:{lesson.pk}'
    draft=CodeDraft.objects.filter(user=request.user,key=key).first()
    done=set(LessonCompletion.objects.filter(user=request.user).values_list('lesson_id',flat=True))
    return render(request,'core/lesson_detail.html',{'lesson':lesson,'all_lessons':lessons,
            'prev_lesson':next((l for l in reversed(lessons) if l.order<lesson.order),None),
            'next_lesson':next((l for l in lessons if l.order>lesson.order),None),'completed_ids':done,'is_complete':lesson.pk in done,
            'editor_code':draft.code if draft else lesson.starter_code,'starter_code':lesson.starter_code,
            'engine':lesson.language.engine,'draft_key':key,'context_id':lesson.pk,'context_kind':'lesson','active_nav':'languages'})

@login_required
def try_it(request,pk):return redirect('lesson_detail',pk=pk)

@login_required
@require_POST
def lesson_complete(request,pk):
    lesson=get_object_or_404(Lesson,pk=pk);LessonCompletion.objects.get_or_create(user=request.user,lesson=lesson)
    p,_=UserProgress.objects.get_or_create(user=request.user,language=lesson.language)
    p.current_lesson=max(p.current_lesson,lesson.order);p.save(update_fields=['current_lesson'])
    messages.success(request,'Lesson marked complete. You can revisit it at any time.')
    return redirect('lesson_detail',pk=pk)

@login_required
def hardware_list(request):
    return render(request,'core/hardware_list.html',{'systems':HardwareSystem.objects.annotate(lab_count=Count('challenges')).order_by('unlock_order'),
            'active_nav':'hardware'})

@login_required
def hardware_detail(request,slug):
    system=get_object_or_404(HardwareSystem,slug=slug)
    return render(request,'core/hardware_detail.html',{'system':system,'challenges':system.challenges.select_related('language').order_by('order'),
            'completed_ids':set(HardwareProgress.objects.filter(user=request.user,completed=True).values_list('challenge_id',flat=True)),'active_nav':'hardware'})

@login_required
def hardware_challenge(request,slug,challenge_pk):
    system=get_object_or_404(HardwareSystem,slug=slug)
    lab=get_object_or_404(HardwareChallenge,pk=challenge_pk,system=system)
    engine='assembly' if request.GET.get('lang') in ('asm','assembly') else 'c'
    starter=lab.starter_code_asm if engine=='assembly' else lab.starter_code_c;key=f'lab:{lab.pk}:{engine}'
    draft=CodeDraft.objects.filter(user=request.user,key=key).first()
    return render(request,'core/hardware_challenge.html',{'system':system,'challenge':lab,'lab':lab,'engine':engine,
            'starter_code':starter,'editor_code':draft.code if draft else starter,'draft_key':key,'context_id':lab.pk,
            'context_kind':'lab','active_nav':'hardware',
            'component_routes':{component:reverse('hardware_challenge',args=[slug,pk]) for component,pk in system.challenges.values_list('component','pk')}})

@login_required
@require_POST
def hardware_complete(request,slug,challenge_pk):
    lab=get_object_or_404(HardwareChallenge,system__slug=slug,pk=challenge_pk)
    # Configuration completion is earned by server-side state checks during execution.
    if not HardwareProgress.objects.filter(user=request.user,challenge=lab,completed=True).exists():
        messages.info(request,'Run the configuration and pass its state checks to record completion.')
    return redirect('hardware_challenge',slug=slug,challenge_pk=challenge_pk)

@login_required
def playground(request):
    engine=request.GET.get('lang','c')
    if engine not in ENGINES:engine='c'
    first=Lesson.objects.filter(language__engine=engine).order_by('order').first()
    starter=first.starter_code if first else DEFAULT_BOOT if engine=='boot' else 'int main(void){return 0;}'
    key=f'free:{engine}';draft=CodeDraft.objects.filter(user=request.user,key=key).first()
    return render(request,'core/playground.html',{'engine':engine,'starter_code':starter,'editor_code':draft.code if draft else starter,
            'draft_key':key,'context_kind':'free','engines':ENGINES,'active_nav':'playground'})

@login_required
def os_lab(request,pk=None):
    project=get_object_or_404(BootProject,user=request.user,pk=pk) if pk else None
    draft=CodeDraft.objects.filter(user=request.user,key='boot').first()
    code=project.source if project and project.source else draft.code if draft else DEFAULT_BOOT
    return render(request,'core/os_lab.html',{'projects':request.user.boot_projects.all(),'project':project,'engine':'boot',
            'starter_code':DEFAULT_BOOT,'editor_code':code,'draft_key':'boot','context_kind':'boot','active_nav':'os'})


def json_input(request):
    if not request.user.is_authenticated:return None,JsonResponse({'error':'Sign in to use your workspace.'},status=401)
    if len(request.body)>100000:return None,JsonResponse({'error':'Request is too large.'},status=413)
    try:
        data=json.loads(request.body)
        if not isinstance(data,dict):raise ValueError()
        return data,None
    except (ValueError,UnicodeDecodeError):return None,JsonResponse({'error':'Send a JSON object.'},status=400)


def state_checks(result,expected):
    checks=[];state=result.get('state',{})
    for section,values in expected.items():
        if section=='output':
            ok=result['output'].strip()==str(values).strip();checks.append({'name':'Expected output','passed':ok,'expected':str(values).strip(),'actual':result['output'].strip()});continue
        if section=='contains':
            checks.append({'name':'Output contains '+str(values),'passed':str(values) in result['output']});continue
        if section=='truth_table':
            actual=state.get('truth_table',[]);checks.append({'name':'Truth table','passed':actual==values});continue
        for key,value in values.items():
            actual=state.get(section,{}).get(key)
            checks.append({'name':section+' / '+key,'passed':actual==value,'expected':value,'actual':actual})
    return checks

@require_POST
def execute_api(request):
    data,error=json_input(request)
    if error:return error
    engine=data.get('language','c');code=data.get('code','')
    if not isinstance(engine,str):return JsonResponse({'error':'Language must be a string.'},status=400)
    minute_key='run:'+str(request.user.pk)
    count=cache.get(minute_key,0)
    if count>=60:return JsonResponse({'error':'Execution limit: 60 runs per minute. Try again shortly.'},status=429)
    cache.set(minute_key,count+1,60)
    context=data.get('context_kind','free');pk=data.get('context_id');expected={};lab=None
    if context in ('lesson','lab') and (isinstance(pk,bool) or not isinstance(pk,(int,str)) or not str(pk).isdigit() or int(pk)<1):
        return JsonResponse({'error':'Use a positive numeric context ID.'},status=400)
    if context=='lesson':
        lesson=get_object_or_404(Lesson,pk=pk)
        if lesson.language.engine!=engine:return JsonResponse({'error':'Use the lesson language.'},status=400)
        expected=lesson.expected_state
    elif context=='lab':
        lab=get_object_or_404(HardwareChallenge,pk=pk)
        if engine not in ('c','assembly'):return JsonResponse({'error':'Configurations support C or RV32I assembly.'},status=400)
        expected=lab.expected_state
    elif context not in ('free','boot'):return JsonResponse({'error':'Unknown workspace context.'},status=400)
    r=execute(code,engine);checks=state_checks(r,expected) if not r['errors'] else []
    
    if lab:
        from .hardware_sim import effects
        r['model']=effects(lab,r.get('state',{}))
    r['checks']=checks;r['passed']=bool(checks) and all(c['passed'] for c in checks) and not r['errors']
    if lab and r['passed']:
        HardwareProgress.objects.update_or_create(user=request.user,challenge=lab,defaults={'completed':True,'language_used':engine})
    return JsonResponse(r)

@require_POST
def draft_api(request):
    data,error=json_input(request)
    if error:return error
    key=data.get('key','');code=data.get('code','')
    if not isinstance(key,str) or not re.fullmatch(r'lesson:\d+|lab:\d+:(c|assembly)|free:(c|assembly|machine|rust|verilog|boot)|boot',key):return JsonResponse({'error':'Invalid draft key.'},status=400)
    if not isinstance(code,str) or len(code.encode())>24000:return JsonResponse({'error':'Draft limit is 24 KB.'},status=400)
    CodeDraft.objects.update_or_create(user=request.user,key=key,defaults={'code':code})
    return JsonResponse({'saved':True})

@require_POST
def boot_save_api(request):
    data,error=json_input(request)
    if error:return error
    code=data.get('code');name=data.get('name','Untitled boot sector')
    if not isinstance(name,str) or not name.strip() or len(name)>80:return JsonResponse({'error':'Use a project name of 1–80 characters.'},status=400)
    r=execute(code,'boot')
    if r['errors']:return JsonResponse({'error':r['errors'][0]},status=400)
    pk=data.get('project_id')
    if pk and (isinstance(pk,bool) or not isinstance(pk,(int,str)) or not str(pk).isdigit()):return JsonResponse({'error':'Invalid project ID.'},status=400)
    if pk:project=get_object_or_404(BootProject,user=request.user,pk=pk)
    else:project=BootProject(user=request.user)
    project.name=name.strip();project.source=code;project.image_hex=r['image_hex'];project.save()
    return JsonResponse({'saved':True,'id':project.pk,'url':reverse('os_project',args=[project.pk]),'download':reverse('boot_download',args=[project.pk])})

@login_required
@require_POST
def boot_upload(request):
    upload=request.FILES.get('image');name=request.POST.get('name','Imported boot sector')[:80].strip() or 'Imported boot sector'
    if not upload or upload.size!=512:
        messages.error(request,'Upload an exact 512-byte BIOS boot sector.');return redirect('os_lab')
    image=upload.read(513)
    if len(image)!=512 or image[510:]!=b'\x55\xaa':
        messages.error(request,'Invalid BIOS signature. Expected 55 AA in the final two bytes.');return redirect('os_lab')
    project=BootProject.objects.create(user=request.user,name=name,image_hex=image.hex())
    messages.success(request,'Image hosted in your workspace. Boot it with the Boot saved image button.');return redirect('os_project',pk=project.pk)

@login_required
def boot_download(request,pk):
    p=get_object_or_404(BootProject,user=request.user,pk=pk)
    return HttpResponse(bytes.fromhex(p.image_hex),content_type='application/octet-stream',headers={'Content-Disposition':f'attachment; filename="boot-{p.pk}.img"'})

@login_required
@require_POST
def boot_run_api(request,pk):
    p=get_object_or_404(BootProject,user=request.user,pk=pk)
    try:r=BootVM(bytes.fromhex(p.image_hex)).run()
    except RunError as e:return JsonResponse({'error':str(e)},status=400)
    return JsonResponse(r)

@login_required
@require_POST
def boot_delete(request,pk):
    get_object_or_404(BootProject,user=request.user,pk=pk).delete();messages.success(request,'Boot project deleted.');return redirect('os_lab')
