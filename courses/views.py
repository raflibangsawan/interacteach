from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Course, Module, Lesson, Enrollment, LessonProgress

@login_required
def course_list(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    level_filter = request.GET.get('level', '')
    
    # Start with all courses
    courses = Course.objects.all()
    
    # Apply search filter if provided
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Apply level filter if provided
    if level_filter:
        courses = courses.filter(level=level_filter)
    
    # Get all available levels for the filter dropdown
    levels = Course.objects.values_list('level', flat=True).distinct()
    
    context = {
        'courses': courses,
        'search_query': search_query,
        'level_filter': level_filter,
        'levels': levels
    }
    
    return render(request, 'courses/course_list.html', context)

@login_required
def course_detail(request, course_slug):
    # Get the course or return 404
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if the user is enrolled
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    # Get all modules and lessons for the course
    modules = Module.objects.filter(course=course).prefetch_related('lessons')
    
    # Calculate course progress if enrolled
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
            progress_width = f"{int(progress_percentage)}%"
    
    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'progress_percentage': progress_percentage,
        'progress_width': progress_width
    }
    
    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_course(request, course_slug):
    if request.method == 'POST':
        course = get_object_or_404(Course, slug=course_slug)
        
        # Check if already enrolled
        if Enrollment.objects.filter(user=request.user, course=course).exists():
            messages.info(request, f"You are already enrolled in {course.title}")
        else:
            # Create enrollment
            enrollment = Enrollment.objects.create(user=request.user, course=course)
            messages.success(request, f"Successfully enrolled in {course.title}")
        
        return redirect('courses:course_detail', course_slug=course_slug)
    
    return redirect('courses:course_list')

@login_required
def lesson_detail(request, course_slug, lesson_id):
    # Get the course and lesson or return 404
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    
    # Check if the user is enrolled
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
    except Enrollment.DoesNotExist:
        messages.error(request, "You must be enrolled in this course to view lessons")
        return redirect('courses:course_detail', course_slug=course_slug)
    
    # Get or create lesson progress
    lesson_progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    
    # Mark as completed if requested
    if request.method == 'POST' and 'mark_completed' in request.POST:
        lesson_progress.completed = True
        lesson_progress.save()
        messages.success(request, f"Lesson '{lesson.title}' marked as completed")
        
        # Check if all lessons are completed to mark the course as completed
        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment, 
            completed=True
        ).count()
        
        if total_lessons == completed_lessons:
            enrollment.completed = True
            enrollment.save()
            messages.success(request, f"Congratulations! You've completed the course '{course.title}'")
    
    # Get the next and previous lessons for navigation
    module = lesson.module
    lessons_in_module = list(module.lessons.all())
    current_index = lessons_in_module.index(lesson)
    
    prev_lesson = lessons_in_module[current_index - 1] if current_index > 0 else None
    next_lesson = lessons_in_module[current_index + 1] if current_index < len(lessons_in_module) - 1 else None
    
    # If no next lesson in current module, check if there's another module
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
    
    return render(request, 'courses/lesson_detail.html', context)

@login_required
def my_courses(request):
    # Get all courses the user is enrolled in
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    
    # Calculate progress for each enrollment
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
    
    return render(request, 'courses/my_courses.html', context)

