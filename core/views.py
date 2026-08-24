import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm
from .models import Language, Lesson, LessonCompletion, HardwareSystem, HardwareChallenge, HardwareProgress
from .services import execute_code


def landing(request):
    return render(request, 'core/landing.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('language_list')
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('language_list')
            form.add_error(None, 'Invalid credentials.')
    return render(request, 'core/login.html', {'form': form})


def register(request):
    if request.user.is_authenticated:
        return redirect('language_list')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm = form.cleaned_data['confirm_password']
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Username already taken.')
            elif password != confirm:
                form.add_error('confirm_password', 'Passwords do not match.')
            else:
                User.objects.create_user(username=username, email=email, password=password)
                return redirect('login')
    return render(request, 'core/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    return redirect('language_list')


@login_required(login_url='login')
def language_list(request):
    languages = Language.objects.all()
    return render(request, 'core/language_list.html', {'languages': languages})


@login_required(login_url='login')
def language_detail(request, pk):
    language = get_object_or_404(Language, pk=pk)
    lessons = language.lessons.all()
    completed_ids = LessonCompletion.objects.filter(
        user=request.user, lesson__language=language
    ).values_list('lesson_id', flat=True)
    return render(request, 'core/language_detail.html', {
        'language': language,
        'lessons': lessons,
        'completed_ids': list(completed_ids),
    })


@login_required(login_url='login')
def lesson_detail(request, pk, lesson_order):
    language = get_object_or_404(Language, pk=pk)
    lesson = get_object_or_404(Lesson, language=language, order=lesson_order)
    all_lessons = language.lessons.all()
    completed_ids = LessonCompletion.objects.filter(
        user=request.user, lesson__language=language
    ).values_list('lesson_id', flat=True)
    return render(request, 'core/lesson_detail.html', {
        'current_language': language,
        'lesson': lesson,
        'all_lessons': all_lessons,
        'completed_ids': list(completed_ids),
    })


@login_required(login_url='login')
def lesson_complete(request, pk, lesson_order):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    language = get_object_or_404(Language, pk=pk)
    lesson = get_object_or_404(Lesson, language=language, order=lesson_order)
    LessonCompletion.objects.get_or_create(user=request.user, lesson=lesson)
    next_lesson = language.lessons.filter(order=lesson_order + 1).first()
    if next_lesson:
        return redirect('lesson_detail', pk=language.pk, lesson_order=next_lesson.order)
    return redirect('language_detail', pk=language.pk)


@login_required(login_url='login')
def run_code(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    data = json.loads(request.body)
    result = execute_code(
        data.get('language', 'C'),
        data.get('code', ''),
        data.get('architecture', 'x86-64')
    )
    return JsonResponse(result)


def try_it(request):
    return render(request, 'core/try_it.html', {
        'initial_language': request.GET.get('lang', 'C'),
        'initial_code': request.GET.get('code', ''),
    })


@login_required(login_url='login')
def hardware_list(request):
    systems = HardwareSystem.objects.all().order_by('unlock_order')
    if request.user.is_staff:
        is_locked = False
    else:
        count = LessonCompletion.objects.filter(user=request.user).count()
        is_locked = count < 5
    return render(request, 'core/hardware_list.html', {
        'systems': systems,
        'is_locked': is_locked,
    })

@login_required(login_url='login')
def hardware_detail(request, slug):
    system = get_object_or_404(HardwareSystem, slug=slug)
    challenges = system.challenges.all()
    completed_ids = HardwareProgress.objects.filter(
        user=request.user, completed=True
    ).values_list('challenge_id', flat=True)
    return render(request, 'core/hardware_detail.html', {
        'system': system,
        'challenges': challenges,
        'completed_ids': list(completed_ids),
    })


@login_required(login_url='login')
def hardware_challenge(request, slug, challenge_pk):
    system = get_object_or_404(HardwareSystem, slug=slug)
    challenge = get_object_or_404(HardwareChallenge, pk=challenge_pk, system=system)
    lang = request.GET.get('lang', 'c')
    arch = request.GET.get('arch', 'x86-64')
    if lang == 'arm':
        starter = challenge.starter_code_asm_arm
        arch = 'arm64'
    elif lang == 'asm':
        starter = challenge.starter_code_asm_x86
    else:
        starter = challenge.starter_code_c
    return render(request, 'core/hardware_challenge.html', {
        'system': system,
        'challenge': challenge,
        'lang': lang,
        'arch': arch,
        'starter_code': starter,
    })


@login_required(login_url='login')
def hardware_complete(request, slug, challenge_pk):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    system = get_object_or_404(HardwareSystem, slug=slug)
    challenge = get_object_or_404(HardwareChallenge, pk=challenge_pk, system=system)
    progress, _ = HardwareProgress.objects.get_or_create(user=request.user, challenge=challenge)
    progress.completed = True
    progress.language_used = request.POST.get('language', 'c')
    progress.save()
    next_challenge = system.challenges.filter(order__gt=challenge.order).first()
    if next_challenge:
        return redirect('hardware_challenge', slug=slug, challenge_pk=next_challenge.pk)
    return redirect('hardware_detail', slug=slug)
