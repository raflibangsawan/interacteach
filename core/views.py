from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from courses.models import Course, Module, Lesson, Enrollment, LessonProgress
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created successfully! You can now log in.")
            return redirect('core:login')
    else:
        form = SignUpForm()
    
    return render(request, 'core/signup.html', {'form': form})

@login_required
def home(request):
    latest_courses = Course.objects.all().order_by('-created_at')[:6]
    
    enrolled_courses = []
    if request.user.is_authenticated:
        enrolled_courses = Course.objects.filter(
            enrollments__user=request.user
        ).order_by('-enrollments__enrolled_at')[:3]
    
    context = {
        'latest_courses': latest_courses,
        'enrolled_courses': enrolled_courses
    }
    
    return render(request, 'core/home.html', context)

def logout_view(request):
    logout(request)
    return redirect('core:login')

@login_required
def course_list(request):
    search_query = request.GET.get('search', '')
    
    courses = Course.objects.all()
    
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    context = {
        'courses': courses,
        'search_query': search_query,
    }
    
    return render(request, 'core/course_list.html', context)

@login_required
def course_detail(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    modules = Module.objects.filter(course=course).prefetch_related('lessons')
    
    progress_percentage = 0
    progress_width = "0%" 
    
    if is_enrolled:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment, 
            completed=True
        ).count()
        
        total_lessons = Lesson.objects.filter(module__course=course).count()
        
        if total_lessons > 0:
            progress_percentage = (completed_lessons / total_lessons) * 100
            progress_width = f"{int(progress_percentage)}%"  # Format as CSS width value
    
    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'progress_percentage': progress_percentage,
        'progress_width': progress_width
    }
    
    return render(request, 'core/course_detail.html', context)

@login_required
def enroll_course(request, course_slug):
    if request.method == 'POST':
        course = get_object_or_404(Course, slug=course_slug)
        
        if Enrollment.objects.filter(user=request.user, course=course).exists():
            messages.info(request, f"You are already enrolled in {course.title}")
        else:
            enrollment = Enrollment.objects.create(user=request.user, course=course)
            messages.success(request, f"Successfully enrolled in {course.title}")
        
        return redirect('course_detail', course_slug=course_slug)
    
    return redirect('course_list')

@login_required
def lesson_detail(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
    except Enrollment.DoesNotExist:
        messages.error(request, "You must be enrolled in this course to view lessons")
        return redirect('course_detail', course_slug=course_slug)
    
    lesson_progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    
    if request.method == 'POST' and 'mark_completed' in request.POST:
        lesson_progress.completed = True
        lesson_progress.save()
        messages.success(request, f"Lesson '{lesson.title}' marked as completed")
        
        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment, 
            completed=True
        ).count()
        
        if total_lessons == completed_lessons:
            enrollment.completed = True
            enrollment.save()
            messages.success(request, f"Congratulations! You've completed the course '{course.title}'")
    
    module = lesson.module
    lessons_in_module = list(module.lessons.all())
    current_index = lessons_in_module.index(lesson)
    
    prev_lesson = lessons_in_module[current_index - 1] if current_index > 0 else None
    next_lesson = lessons_in_module[current_index + 1] if current_index < len(lessons_in_module) - 1 else None
    
    if not next_lesson:
        modules = list(Module.objects.filter(course=course))
        current_module_index = modules.index(module)
        
        if current_module_index < len(modules) - 1:
            next_module = modules[current_module_index + 1]
            next_module_first_lesson = next_module.lessons.first()
            if next_module_first_lesson:
                next_lesson = next_module_first_lesson
    
    context = {
        'course': course,
        'lesson': lesson,
        'is_completed': lesson_progress.completed,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'module': module
    }
    
    return render(request, 'core/lesson_detail.html', context)

@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    
    for enrollment in enrollments:
        total_lessons = Lesson.objects.filter(module__course=enrollment.course).count()
        if total_lessons > 0:
            completed_lessons = LessonProgress.objects.filter(
                enrollment=enrollment, 
                completed=True
            ).count()
            enrollment.progress_percentage = (completed_lessons / total_lessons) * 100
            enrollment.progress_width = f"{int(enrollment.progress_percentage)}%"
        else:
            enrollment.progress_percentage = 0
            enrollment.progress_width = "0%"
    
    context = {
        'enrollments': enrollments
    }
    
    return render(request, 'core/my_courses.html', context)


def register(request):
    test_tampil = ['elemen1', 'elemen2', 'elemen3']
    test2 = 10000 * 5

    context = {
        'variable': test_tampil,
        'variable2': test2
    }

    return render(request, 'core/register.html', context)

def csrf_failure(request, reason=""):
    response = render(request, '403.html')
    response.status_code = 403
    return response

def handler403(request, exception=None):
    response = render(request, '403.html')
    response.status_code = 403
    return response

def handler404(request, exception=None):
    response = render(request, '404.html')
    response.status_code = 404
    return response

def handler500(request):
    response = render(request, '500.html')
    response.status_code = 500
    return response