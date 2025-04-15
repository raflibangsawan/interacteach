from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Course, Module, Lesson, Enrollment, LessonProgress, InstructorProfile
from .forms import CourseForm, ModuleForm, LessonForm, InstructorProfileForm

@login_required
def course_list(request):
    search_query = request.GET.get('search', '')
    
    courses = Course.objects.filter(is_published=True)
    
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    is_instructor = False
    if request.user.is_authenticated:
        is_instructor = hasattr(request.user, 'instructor_profile')
    
    context = {
        'courses': courses,
        'search_query': search_query,
        'is_instructor': is_instructor,
    }
    
    return render(request, 'courses/course_list.html', context)

@login_required
def course_detail(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    
    if not course.is_published:
        if not (request.user.is_staff or 
                (course.instructor_user and course.instructor_user == request.user)):
            messages.error(request, "This course is not yet published.")
            return redirect('courses:course_list')
    
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    is_instructor = course.instructor_user == request.user
    
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
            progress_width = f"{int(progress_percentage)}%"
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'is_instructor': is_instructor,
        'progress_percentage': progress_percentage,
        'progress_width': progress_width,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_course(request, course_slug):
    if request.method == 'POST':
        course = get_object_or_404(Course, slug=course_slug)
        
        if not course.is_published:
            messages.error(request, "You cannot enroll in an unpublished course.")
            return redirect('courses:course_list')
        
        if Enrollment.objects.filter(user=request.user, course=course).exists():
            messages.info(request, f"You are already enrolled in {course.title}")
        else:
            enrollment = Enrollment.objects.create(user=request.user, course=course)
            messages.success(request, f"Successfully enrolled in {course.title}")
        
        return redirect('courses:course_detail', course_slug=course_slug)
    
    return redirect('courses:course_list')

@login_required
def lesson_detail(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    
    if not course.is_published:
        if not (request.user.is_staff or 
                (course.instructor_user and course.instructor_user == request.user)):
            messages.error(request, "This course is not yet published.")
            return redirect('courses:course_list')
    
    is_instructor = course.instructor_user == request.user
    
    if not is_instructor:
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
        except Enrollment.DoesNotExist:
            messages.error(request, "You must be enrolled in this course to view lessons")
            return redirect('courses:course_detail', course_slug=course_slug)
        
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
        
        is_completed = lesson_progress.completed
    else:
        is_completed = False
    
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
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'course': course,
        'lesson': lesson,
        'is_completed': is_completed,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'module': module,
        'is_instructor': is_instructor,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/lesson_detail.html', context)

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
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'enrollments': enrollments,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/my_courses.html', context)

# Instructor Views
@login_required
def instructor_dashboard(request):
    try:
        instructor_profile = InstructorProfile.objects.get(user=request.user)
    except InstructorProfile.DoesNotExist:
        return redirect('courses:become_instructor')
    
    courses = Course.objects.filter(instructor_user=request.user)
    
    total_enrollments = Enrollment.objects.filter(course__instructor_user=request.user).count()
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'instructor_profile': instructor_profile,
        'courses': courses,
        'total_enrollments': total_enrollments,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/dashboard.html', context)

@login_required
def become_instructor(request):
    if InstructorProfile.objects.filter(user=request.user).exists():
        return redirect('courses:instructor_dashboard')
    
    if request.method == 'POST':
        form = InstructorProfileForm(request.POST)
        if form.is_valid():
            instructor_profile = form.save(commit=False)
            instructor_profile.user = request.user
            instructor_profile.save()
            
            messages.success(request, "You are now an instructor! You can create and manage courses.")
            return redirect('courses:instructor_dashboard')
    else:
        form = InstructorProfileForm()
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'form': form,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/become_instructor.html', context)

@login_required
def instructor_courses(request):
    if not InstructorProfile.objects.filter(user=request.user).exists():
        return redirect('courses:become_instructor')
    
    courses = Course.objects.filter(instructor_user=request.user)
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'courses': courses,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/courses.html', context)

@login_required
def create_course(request):
    if not InstructorProfile.objects.filter(user=request.user).exists():
        return redirect('courses:become_instructor')
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor_user = request.user
            course.instructor = request.user.get_full_name() or request.user.username
            course.save()
            
            messages.success(request, f"Course '{course.title}' created successfully!")
            return redirect('courses:edit_course', course_slug=course.slug)
    else:
        form = CourseForm()
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'form': form,
        'is_new': True,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/edit_course.html', context)

@login_required
def edit_course(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to edit this course.")
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.title}' updated successfully!")
            return redirect('courses:instructor_courses')
    else:
        form = CourseForm(instance=course)
    
    modules = Module.objects.filter(course=course).prefetch_related('lessons')
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'form': form,
        'course': course,
        'modules': modules,
        'is_new': False,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/edit_course.html', context)

@login_required
def create_module(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to edit this course.")
    
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            
            last_module = Module.objects.filter(course=course).order_by('-order').first()
            module.order = (last_module.order + 1) if last_module else 1
            
            module.save()
            
            messages.success(request, f"Module '{module.title}' created successfully!")
            return redirect('courses:edit_course', course_slug=course.slug)
    else:
        form = ModuleForm()
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'form': form,
        'course': course,
        'is_new': True,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/edit_module.html', context)

@login_required
def edit_module(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to edit this course.")
    
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, f"Module '{module.title}' updated successfully!")
            return redirect('courses:edit_course', course_slug=course.slug)
    else:
        form = ModuleForm(instance=module)
    
    lessons = Lesson.objects.filter(module=module)
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'form': form,
        'course': course,
        'module': module,
        'lessons': lessons,
        'is_new': False,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/edit_module.html', context)

@login_required
def create_lesson(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to edit this course.")
    
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            
            last_lesson = Lesson.objects.filter(module=module).order_by('-order').first()
            lesson.order = (last_lesson.order + 1) if last_lesson else 1
            
            lesson.save()
            
            messages.success(request, f"Lesson '{lesson.title}' created successfully!")
            return redirect('courses:edit_module', course_slug=course.slug, module_id=module.id)
    else:
        form = LessonForm()
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'form': form,
        'course': course,
        'module': module,
        'is_new': True,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/edit_lesson.html', context)

@login_required
def edit_lesson(request, course_slug, module_id, lesson_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, module=module)
    
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to edit this course.")
    
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lesson '{lesson.title}' updated successfully!")
            return redirect('courses:edit_module', course_slug=course.slug, module_id=module.id)
    else:
        form = LessonForm(instance=lesson)
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'form': form,
        'course': course,
        'module': module,
        'lesson': lesson,
        'is_new': False,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/edit_lesson.html', context)

@login_required
def delete_course(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to delete this course.")
    
    if request.method == 'POST':
        course_title = course.title
        course.delete()
        messages.success(request, f"Course '{course_title}' deleted successfully!")
        return redirect('courses:instructor_courses')
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'course': course,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/delete_course.html', context)

@login_required
def delete_module(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to delete this module.")
    
    if request.method == 'POST':
        module_title = module.title
        module.delete()
        messages.success(request, f"Module '{module_title}' deleted successfully!")
        return redirect('courses:edit_course', course_slug=course.slug)
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'course': course,
        'module': module,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/delete_module.html', context)

@login_required
def delete_lesson(request, course_slug, module_id, lesson_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, module=module)
    
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to delete this lesson.")
    
    if request.method == 'POST':
        lesson_title = lesson.title
        lesson.delete()
        messages.success(request, f"Lesson '{lesson_title}' deleted successfully!")
        return redirect('courses:edit_module', course_slug=course.slug, module_id=module.id)
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'course': course,
        'module': module,
        'lesson': lesson,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/delete_lesson.html', context)

@login_required
def publish_course(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to publish this course.")
    
    if request.method == 'POST':
        course.is_published = True
        course.save()
        messages.success(request, f"Course '{course.title}' published successfully!")
        return redirect('courses:instructor_courses')
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'course': course,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/publish_course.html', context)

@login_required
def unpublish_course(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to unpublish this course.")
    
    if request.method == 'POST':
        course.is_published = False
        course.save()
        messages.success(request, f"Course '{course.title}' unpublished successfully!")
        return redirect('courses:instructor_courses')
    
    is_instructor_profile = False
    if request.user.is_authenticated:
        is_instructor_profile = hasattr(request.user, 'instructor_profile')
    
    context = {
        'course': course,
        'is_instructor_profile': is_instructor_profile,
    }
    
    return render(request, 'courses/instructor/unpublish_course.html', context)

