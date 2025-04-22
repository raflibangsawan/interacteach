from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, Max
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.forms import inlineformset_factory
from django.db import transaction
from django.urls import reverse

from .models import (
    Course, Module, Lesson, Enrollment, LessonProgress, InstructorProfile, 
    ForumThread, ForumReply, Quiz, Question, Choice, QuizAttempt, QuizResponse
)
from .forms import (
    CourseForm, ModuleForm, LessonForm, InstructorProfileForm, 
    ForumThreadForm, ForumReplyForm, QuizForm, QuestionForm, ChoiceFormSet, QuizResponseForm
)

@login_required
def course_list(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    
    # Start with all published courses
    courses = Course.objects.filter(is_published=True)
    
    # Apply search filter if provided
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    context = {
        'courses': courses,
        'search_query': search_query,
    }
    
    return render(request, 'courses/course_list.html', context)


@login_required
def course_detail(request, course_slug):
    # Get the course or return 404
    course = get_object_or_404(Course, slug=course_slug)
    
    # If course is not published, only allow instructor or admin to view it
    if not course.is_published:
        if not (request.user.is_staff or 
                (course.instructor_user and course.instructor_user == request.user)):
            messages.error(request, "This course is not yet published.")
            return redirect('courses:course_list')
    
    # Check if the user is enrolled
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    # Check if the user is the instructor
    is_instructor = course.instructor_user == request.user
    
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
        'is_instructor': is_instructor,
        'progress_percentage': progress_percentage,
        'progress_width': progress_width,
    }
    
    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_course(request, course_slug):
    if request.method == 'POST':
        course = get_object_or_404(Course, slug=course_slug)
        
        # Only allow enrollment in published courses
        if not course.is_published:
            messages.error(request, "You cannot enroll in an unpublished course.")
            return redirect('courses:course_list')
        
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
    
    # If course is not published, only allow instructor or admin to view it
    if not course.is_published:
        if not (request.user.is_staff or 
                (course.instructor_user and course.instructor_user == request.user)):
            messages.error(request, "This course is not yet published.")
            return redirect('courses:course_list')
    
    # Check if the user is enrolled or is the instructor
    is_instructor = course.instructor_user == request.user
    
    if not is_instructor:
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
        
        is_completed = lesson_progress.completed
    else:
        # Instructor doesn't need to track progress
        is_completed = False
    
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
        'is_completed': is_completed,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'module': module,
        'is_instructor': is_instructor,
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
        'enrollments': enrollments,
    }
    
    return render(request, 'courses/my_courses.html', context)

# Instructor views
@login_required
def instructor_dashboard(request):
    # Check if user is an instructor
    try:
        instructor_profile = InstructorProfile.objects.get(user=request.user)
    except InstructorProfile.DoesNotExist:
        # If not an instructor, redirect to become instructor page
        return redirect('courses:become_instructor')
    
    # Get all courses created by this instructor
    courses = Course.objects.filter(instructor_user=request.user)
    
    # Get enrollment statistics
    total_enrollments = Enrollment.objects.filter(course__instructor_user=request.user).count()
    
    context = {
        'instructor_profile': instructor_profile,
        'courses': courses,
        'total_enrollments': total_enrollments,
    }
    
    return render(request, 'courses/instructor/dashboard.html', context)

@login_required
def become_instructor(request):
    # Check if user is already an instructor
    if InstructorProfile.objects.filter(user=request.user).exists():
        return redirect('courses:instructor_dashboard')
    
    if request.method == 'POST':
        form = InstructorProfileForm(request.POST)
        if form.is_valid():
            # Create instructor profile
            instructor_profile = form.save(commit=False)
            instructor_profile.user = request.user
            instructor_profile.save()
            
            messages.success(request, "You are now an instructor! You can create and manage courses.")
            return redirect('courses:instructor_dashboard')
    else:
        form = InstructorProfileForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'courses/instructor/become_instructor.html', context)

@login_required
def instructor_courses(request):
    # Check if user is an instructor
    if not InstructorProfile.objects.filter(user=request.user).exists():
        return redirect('courses:become_instructor')
    
    # Get all courses created by this instructor
    courses = Course.objects.filter(instructor_user=request.user)
    
    context = {
        'courses': courses,
    }
    
    return render(request, 'courses/instructor/courses.html', context)

@login_required
def create_course(request):
    # Check if user is an instructor
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
    
    context = {
        'form': form,
        'is_new': True,
    }
    
    return render(request, 'courses/instructor/edit_course.html', context)

@login_required
def edit_course(request, course_slug):
    # Get the course or return 404
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is the instructor of this course
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
    
    # Get all modules for this course
    modules = Module.objects.filter(course=course).prefetch_related('lessons')
    
    context = {
        'form': form,
        'course': course,
        'modules': modules,
        'is_new': False,
    }
    
    return render(request, 'courses/instructor/edit_course.html', context)

@login_required
def create_module(request, course_slug):
    # Get the course or return 404
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to edit this course.")
    
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            
            # Set order to be the next available number
            last_module = Module.objects.filter(course=course).order_by('-order').first()
            module.order = (last_module.order + 1) if last_module else 1
            
            module.save()
            
            messages.success(request, f"Module '{module.title}' created successfully!")
            return redirect('courses:edit_course', course_slug=course.slug)
    else:
        form = ModuleForm()
    
    context = {
        'form': form,
        'course': course,
        'is_new': True,
    }
    
    return render(request, 'courses/instructor/edit_module.html', context)

# Update the edit_module view to include quiz information
@login_required
def edit_module(request, course_slug, module_id):
    # Get the course and module or return 404
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if user is the instructor of this course
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
    
    # Get all lessons for this module
    lessons = Lesson.objects.filter(module=module)
    
    # Check if module has a quiz
    hasattr_module_quiz = hasattr(module, 'quiz')
    
    context = {
        'form': form,
        'course': course,
        'module': module,
        'lessons': lessons,
        'is_new': False,
        'hasattr_module_quiz': hasattr_module_quiz,
    }
    
    return render(request, 'courses/instructor/edit_module.html', context)

@login_required
def create_lesson(request, course_slug, module_id):
    # Get the course and module or return 404
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to edit this course.")
    
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            
            # Set order to be the next available number
            last_lesson = Lesson.objects.filter(module=module).order_by('-order').first()
            lesson.order = (last_lesson.order + 1) if last_lesson else 1
            
            lesson.save()
            
            messages.success(request, f"Lesson '{lesson.title}' created successfully!")
            return redirect('courses:edit_module', course_slug=course.slug, module_id=module.id)
    else:
        form = LessonForm()
    
    context = {
        'form': form,
        'course': course,
        'module': module,
        'is_new': True,
    }
    
    return render(request, 'courses/instructor/edit_lesson.html', context)

@login_required
def edit_lesson(request, course_slug, module_id, lesson_id):
    # Get the course, module, and lesson or return 404
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, module=module)
    
    # Check if user is the instructor of this course
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
    
    context = {
        'form': form,
        'course': course,
        'module': module,
        'lesson': lesson,
        'is_new': False,
    }
    
    return render(request, 'courses/instructor/edit_lesson.html', context)

@login_required
def delete_course(request, course_slug):
    # Get the course or return 404
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to delete this course.")
    
    if request.method == 'POST':
        course_title = course.title
        course.delete()
        messages.success(request, f"Course '{course_title}' deleted successfully!")
        return redirect('courses:instructor_courses')
    
    context = {
        'course': course,
    }
    
    return render(request, 'courses/instructor/delete_course.html', context)

@login_required
def delete_module(request, course_slug, module_id):
    # Get the course and module or return 404
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to delete this module.")
    
    if request.method == 'POST':
        module_title = module.title
        module.delete()
        messages.success(request, f"Module '{module_title}' deleted successfully!")
        return redirect('courses:edit_course', course_slug=course.slug)
    
    context = {
        'course': course,
        'module': module,
    }
    
    return render(request, 'courses/instructor/delete_module.html', context)

@login_required
def delete_lesson(request, course_slug, module_id, lesson_id):
    # Get the course, module, and lesson or return 404
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, module=module)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to delete this lesson.")
    
    if request.method == 'POST':
        lesson_title = lesson.title
        lesson.delete()
        messages.success(request, f"Lesson '{lesson_title}' deleted successfully!")
        return redirect('courses:edit_module', course_slug=course.slug, module_id=module.id)
    
    context = {
        'course': course,
        'module': module,
        'lesson': lesson,
    }
    
    return render(request, 'courses/instructor/delete_lesson.html', context)

@login_required
def publish_course(request, course_slug):
    # Get the course or return 404
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to publish this course.")
    
    if request.method == 'POST':
        course.is_published = True
        course.save()
        messages.success(request, f"Course '{course.title}' published successfully!")
        return redirect('courses:instructor_courses')
    
    context = {
        'course': course,
    }
    
    return render(request, 'courses/instructor/publish_course.html', context)

@login_required
def unpublish_course(request, course_slug):
    # Get the course or return 404
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to unpublish this course.")
    
    if request.method == 'POST':
        course.is_published = False
        course.save()
        messages.success(request, f"Course '{course.title}' unpublished successfully!")
        return redirect('courses:instructor_courses')
    
    context = {
        'course': course,
    }
    
    return render(request, 'courses/instructor/unpublish_course.html', context)

# Forum views
@login_required
def forum_thread_list(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if the user is enrolled or is the instructor
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    is_instructor = course.instructor_user == request.user
    
    if not (is_enrolled or is_instructor or request.user.is_staff):
        messages.error(request, "You must be enrolled in this course to access the forum.")
        return redirect('courses:course_detail', course_slug=course_slug)
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'recent')
    
    # Start with all threads for this course
    threads = ForumThread.objects.filter(course=course)
    
    # Apply search filter if provided
    if search_query:
        threads = threads.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Apply sorting
    if sort_by == 'recent':
        threads = threads.order_by('-is_pinned', '-created_at')
    elif sort_by == 'activity':
        # This is a bit complex as we need to sort by the latest activity (thread creation or latest reply)
        threads = threads.annotate(
            latest_activity=models.Case(
                models.When(replies__isnull=True, then=models.F('created_at')),
                default=models.Subquery(
                    ForumReply.objects.filter(thread=models.OuterRef('pk'))
                    .order_by('-created_at')
                    .values('created_at')[:1]
                ),
                output_field=models.DateTimeField()
            )
        ).order_by('-is_pinned', '-latest_activity')
    elif sort_by == 'replies':
        threads = threads.annotate(reply_count=Count('replies')).order_by('-is_pinned', '-reply_count')
    
    # Add reply counts to each thread
    for thread in threads:
        thread.reply_count = thread.replies.count()
        thread.last_reply = thread.replies.order_by('-created_at').first()
    
    context = {
        'course': course,
        'threads': threads,
        'search_query': search_query,
        'sort_by': sort_by,
        'is_instructor': is_instructor,
    }
    
    return render(request, 'courses/forum/thread_list.html', context)

@login_required
def forum_thread_create(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if the user is enrolled or is the instructor
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    is_instructor = course.instructor_user == request.user
    
    if not (is_enrolled or is_instructor or request.user.is_staff):
        messages.error(request, "You must be enrolled in this course to create forum threads.")
        return redirect('courses:course_detail', course_slug=course_slug)
    
    if request.method == 'POST':
        form = ForumThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.course = course
            thread.user = request.user
            thread.save()
            
            messages.success(request, "Thread created successfully!")
            return redirect('courses:forum_thread_detail', course_slug=course_slug, thread_id=thread.id)
    else:
        form = ForumThreadForm()
    
    context = {
        'course': course,
        'form': form,
    }
    
    return render(request, 'courses/forum/thread_create.html', context)

@login_required
def forum_thread_detail(request, course_slug, thread_id):
    course = get_object_or_404(Course, slug=course_slug)
    thread = get_object_or_404(ForumThread, id=thread_id, course=course)
    
    # Check if the user is enrolled or is the instructor
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    is_instructor = course.instructor_user == request.user
    
    if not (is_enrolled or is_instructor or request.user.is_staff):
        messages.error(request, "You must be enrolled in this course to view forum threads.")
        return redirect('courses:course_detail', course_slug=course_slug)
    
    # Get all replies for this thread
    replies = thread.replies.all()
    
    # Handle reply form
    if request.method == 'POST' and not thread.is_locked:
        form = ForumReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.thread = thread
            reply.user = request.user
            reply.save()
            
            messages.success(request, "Reply posted successfully!")
            return redirect('courses:forum_thread_detail', course_slug=course_slug, thread_id=thread.id)
    else:
        form = ForumReplyForm()
    
    context = {
        'course': course,
        'thread': thread,
        'replies': replies,
        'form': form,
        'is_instructor': is_instructor,
    }
    
    return render(request, 'courses/forum/thread_detail.html', context)

@login_required
def forum_thread_edit(request, course_slug, thread_id):
    course = get_object_or_404(Course, slug=course_slug)
    thread = get_object_or_404(ForumThread, id=thread_id, course=course)
    
    # Check if the user is the thread creator or instructor
    is_instructor = course.instructor_user == request.user
    
    if thread.user != request.user and not (is_instructor or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to edit this thread.")
    
    if request.method == 'POST':
        form = ForumThreadForm(request.POST, instance=thread)
        if form.is_valid():
            form.save()
            
            messages.success(request, "Thread updated successfully!")
            return redirect('courses:forum_thread_detail', course_slug=course_slug, thread_id=thread.id)
    else:
        form = ForumThreadForm(instance=thread)
    
    context = {
        'course': course,
        'thread': thread,
        'form': form,
        'is_edit': True,
    }
    
    return render(request, 'courses/forum/thread_create.html', context)

@login_required
def forum_thread_delete(request, course_slug, thread_id):
    course = get_object_or_404(Course, slug=course_slug)
    thread = get_object_or_404(ForumThread, id=thread_id, course=course)
    
    # Check if the user is the thread creator or instructor
    is_instructor = course.instructor_user == request.user
    
    if thread.user != request.user and not (is_instructor or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to delete this thread.")
    
    if request.method == 'POST':
        thread.delete()
        messages.success(request, "Thread deleted successfully!")
        return redirect('courses:forum_thread_list', course_slug=course_slug)
    
    context = {
        'course': course,
        'thread': thread,
    }
    
    return render(request, 'courses/forum/thread_delete.html', context)

@login_required
def forum_reply_edit(request, course_slug, thread_id, reply_id):
    course = get_object_or_404(Course, slug=course_slug)
    thread = get_object_or_404(ForumThread, id=thread_id, course=course)
    reply = get_object_or_404(ForumReply, id=reply_id, thread=thread)
    
    # Check if the user is the reply creator or instructor
    is_instructor = course.instructor_user == request.user
    
    if reply.user != request.user and not (is_instructor or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to edit this reply.")
    
    if request.method == 'POST':
        form = ForumReplyForm(request.POST, instance=reply)
        if form.is_valid():
            form.save()
            
            messages.success(request, "Reply updated successfully!")
            return redirect('courses:forum_thread_detail', course_slug=course_slug, thread_id=thread.id)
    else:
        form = ForumReplyForm(instance=reply)
    
    context = {
        'course': course,
        'thread': thread,
        'reply': reply,
        'form': form,
    }
    
    return render(request, 'courses/forum/reply_edit.html', context)

@login_required
def forum_reply_delete(request, course_slug, thread_id, reply_id):
    course = get_object_or_404(Course, slug=course_slug)
    thread = get_object_or_404(ForumThread, id=thread_id, course=course)
    reply = get_object_or_404(ForumReply, id=reply_id, thread=thread)
    
    # Check if the user is the reply creator or instructor
    is_instructor = course.instructor_user == request.user
    
    if reply.user != request.user and not (is_instructor or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to delete this reply.")
    
    if request.method == 'POST':
        reply.delete()
        messages.success(request, "Reply deleted successfully!")
        return redirect('courses:forum_thread_detail', course_slug=course_slug, thread_id=thread.id)
    
    context = {
        'course': course,
        'thread': thread,
        'reply': reply,
    }
    
    return render(request, 'courses/forum/reply_delete.html', context)

@login_required
def forum_thread_pin(request, course_slug, thread_id):
    course = get_object_or_404(Course, slug=course_slug)
    thread = get_object_or_404(ForumThread, id=thread_id, course=course)
    
    # Only instructors and staff can pin threads
    is_instructor = course.instructor_user == request.user
    
    if not (is_instructor or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to pin threads.")
    
    thread.is_pinned = not thread.is_pinned
    thread.save()
    
    action = "pinned" if thread.is_pinned else "unpinned"
    messages.success(request, f"Thread {action} successfully!")
    
    return redirect('courses:forum_thread_detail', course_slug=course_slug, thread_id=thread.id)

@login_required
def forum_thread_lock(request, course_slug, thread_id):
    course = get_object_or_404(Course, slug=course_slug)
    thread = get_object_or_404(ForumThread, id=thread_id, course=course)
    
    # Only instructors and staff can lock threads
    is_instructor = course.instructor_user == request.user
    
    if not (is_instructor or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to lock threads.")
    
    thread.is_locked = not thread.is_locked
    thread.save()
    
    action = "locked" if thread.is_locked else "unlocked"
    messages.success(request, f"Thread {action} successfully!")
    
    return redirect('courses:forum_thread_detail', course_slug=course_slug, thread_id=thread.id)

@login_required
def forum_reply_mark_solution(request, course_slug, thread_id, reply_id):
    course = get_object_or_404(Course, slug=course_slug)
    thread = get_object_or_404(ForumThread, id=thread_id, course=course)
    reply = get_object_or_404(ForumReply, id=reply_id, thread=thread)
    
    # Only thread creator, instructors, and staff can mark solutions
    is_instructor = course.instructor_user == request.user
    
    if thread.user != request.user and not (is_instructor or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to mark solutions.")
    
    # Unmark any existing solution
    if reply.is_solution:
        reply.is_solution = False
    else:
        # Unmark any existing solution
        thread.replies.filter(is_solution=True).update(is_solution=False)
        # Mark this reply as solution
        reply.is_solution = True
    
    reply.save()
    
    action = "marked as solution" if reply.is_solution else "unmarked as solution"
    messages.success(request, f"Reply {action} successfully!")
    
    return redirect('courses:forum_thread_detail', course_slug=course_slug, thread_id=thread.id)


# Quiz views for instructors
@login_required
def create_quiz(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to create a quiz for this module.")
    
    # Check if a quiz already exists for this module
    if hasattr(module, 'quiz'):
        messages.warning(request, f"A quiz already exists for module '{module.title}'. You can edit it instead.")
        return redirect('courses:edit_quiz', course_slug=course_slug, module_id=module_id)
    
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.module = module
            quiz.save()
            
            messages.success(request, f"Quiz '{quiz.title}' created successfully! Now add some questions.")
            return redirect('courses:create_question', course_slug=course_slug, module_id=module_id)
    else:
        # Pre-fill the title with the module title
        form = QuizForm(initial={'title': f"Quiz: {module.title}"})
    
    context = {
        'course': course,
        'module': module,
        'form': form,
        'is_new': True,
    }
    
    return render(request, 'courses/instructor/quiz/edit_quiz.html', context)

@login_required
def edit_quiz(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to edit this quiz.")
    
    # Get the quiz or return 404
    try:
        quiz = module.quiz
    except Quiz.DoesNotExist:
        messages.error(request, f"No quiz exists for module '{module.title}'. Create one first.")
        return redirect('courses:create_quiz', course_slug=course_slug, module_id=module_id)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, f"Quiz '{quiz.title}' updated successfully!")
            return redirect('courses:quiz_detail_instructor', course_slug=course_slug, module_id=module_id)
    else:
        form = QuizForm(instance=quiz)
    
    context = {
        'course': course,
        'module': module,
        'quiz': quiz,
        'form': form,
        'is_new': False,
    }
    
    return render(request, 'courses/instructor/quiz/edit_quiz.html', context)

@login_required
def delete_quiz(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to delete this quiz.")
    
    # Get the quiz or return 404
    try:
        quiz = module.quiz
    except Quiz.DoesNotExist:
        messages.error(request, f"No quiz exists for module '{module.title}'.")
        return redirect('courses:edit_course', course_slug=course_slug)
    
    if request.method == 'POST':
        quiz_title = quiz.title
        quiz.delete()
        messages.success(request, f"Quiz '{quiz_title}' deleted successfully!")
        return redirect('courses:edit_course', course_slug=course_slug)
    
    context = {
        'course': course,
        'module': module,
        'quiz': quiz,
    }
    
    return render(request, 'courses/instructor/quiz/delete_quiz.html', context)

@login_required
def quiz_detail_instructor(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to view this quiz's details.")
    
    # Get the quiz or return 404
    try:
        quiz = module.quiz
    except Quiz.DoesNotExist:
        messages.error(request, f"No quiz exists for module '{module.title}'. Create one first.")
        return redirect('courses:create_quiz', course_slug=course_slug, module_id=module_id)
    
    # Get all questions for this quiz
    questions = quiz.questions.all().prefetch_related('choices')
    
    # Get quiz statistics
    attempts = QuizAttempt.objects.filter(quiz=quiz)
    total_attempts = attempts.count()
    avg_score = attempts.filter(completed_at__isnull=False).aggregate(Avg('score'))['score__avg'] or 0
    pass_rate = attempts.filter(passed=True).count() / total_attempts * 100 if total_attempts > 0 else 0
    
    context = {
        'course': course,
        'module': module,
        'quiz': quiz,
        'questions': questions,
        'total_attempts': total_attempts,
        'avg_score': round(avg_score, 1),
        'pass_rate': round(pass_rate, 1),
    }
    
    return render(request, 'courses/instructor/quiz/quiz_detail.html', context)

@login_required
def create_question(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to create questions for this quiz.")
    
    # Get the quiz or return 404
    try:
        quiz = module.quiz
    except Quiz.DoesNotExist:
        messages.error(request, f"No quiz exists for module '{module.title}'. Create one first.")
        return redirect('courses:create_quiz', course_slug=course_slug, module_id=module_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Save the question
                question = form.save(commit=False)
                question.quiz = quiz
                
                # Set order to be the next available number if not specified
                if not question.order:
                    last_question = Question.objects.filter(quiz=quiz).order_by('-order').first()
                    question.order = (last_question.order + 1) if last_question else 1
                
                question.save()
                
                # Process the choices formset
                formset = ChoiceFormSet(request.POST, instance=question)
                if formset.is_valid():
                    # Check that exactly one choice is marked as correct
                    correct_choices = sum(1 for form in formset if form.cleaned_data.get('is_correct'))
                    if correct_choices != 1:
                        formset.non_form_errors().append("Exactly one choice must be marked as correct.")
                        raise forms.ValidationError("Exactly one choice must be marked as correct.")
                    
                    formset.save()
                    messages.success(request, "Question and choices created successfully!")
                    
                    # Redirect to add another question or back to quiz detail
                    if 'add_another' in request.POST:
                        return redirect('courses:create_question', course_slug=course_slug, module_id=module_id)
                    return redirect('courses:quiz_detail_instructor', course_slug=course_slug, module_id=module_id)
                else:
                    # If formset is invalid, delete the question to avoid orphaned questions
                    question.delete()
                    transaction.set_rollback(True)
    else:
        form = QuestionForm()
        formset = ChoiceFormSet()
    
    context = {
        'course': course,
        'module': module,
        'quiz': quiz,
        'form': form,
        'formset': formset,
    }
    
    return render(request, 'courses/instructor/quiz/edit_question.html', context)

@login_required
def edit_question(request, course_slug, module_id, question_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to edit questions for this quiz.")
    
    # Get the quiz or return 404
    try:
        quiz = module.quiz
    except Quiz.DoesNotExist:
        messages.error(request, f"No quiz exists for module '{module.title}'.")
        return redirect('courses:edit_course', course_slug=course_slug)
    
    # Get the question or return 404
    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            with transaction.atomic():
                # Save the question
                question = form.save()
                
                # Process the choices formset
                formset = ChoiceFormSet(request.POST, instance=question)
                if formset.is_valid():
                    # Check that exactly one choice is marked as correct
                    correct_choices = sum(1 for form in formset if form.cleaned_data.get('is_correct'))
                    if correct_choices != 1:
                        formset.non_form_errors().append("Exactly one choice must be marked as correct.")
                        raise forms.ValidationError("Exactly one choice must be marked as correct.")
                    
                    formset.save()
                    messages.success(request, "Question and choices updated successfully!")
                    return redirect('courses:quiz_detail_instructor', course_slug=course_slug, module_id=module_id)
    else:
        form = QuestionForm(instance=question)
        formset = ChoiceFormSet(instance=question)
    
    context = {
        'course': course,
        'module': module,
        'quiz': quiz,
        'question': question,
        'form': form,
        'formset': formset,
        'is_edit': True,
    }
    
    return render(request, 'courses/instructor/quiz/edit_question.html', context)

@login_required
def delete_question(request, course_slug, module_id, question_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if user is the instructor of this course
    if course.instructor_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to delete questions from this quiz.")
    
    # Get the quiz or return 404
    try:
        quiz = module.quiz
    except Quiz.DoesNotExist:
        messages.error(request, f"No quiz exists for module '{module.title}'.")
        return redirect('courses:edit_course', course_slug=course_slug)
    
    # Get the question or return 404
    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, "Question deleted successfully!")
        return redirect('courses:quiz_detail_instructor', course_slug=course_slug, module_id=module_id)
    
    context = {
        'course': course,
        'module': module,
        'quiz': quiz,
        'question': question,
    }
    
    return render(request, 'courses/instructor/quiz/delete_question.html', context)

# Quiz views for students
@login_required
def quiz_detail_student(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if the user is enrolled
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
    except Enrollment.DoesNotExist:
        messages.error(request, "You must be enrolled in this course to take quizzes.")
        return redirect('courses:course_detail', course_slug=course_slug)
    
    # Get the quiz or return 404
    try:
        quiz = module.quiz
    except Quiz.DoesNotExist:
        messages.error(request, f"No quiz exists for module '{module.title}'.")
        return redirect('courses:course_detail', course_slug=course_slug)
    
    # Check if the quiz is published
    if not quiz.is_published and not (course.instructor_user == request.user or request.user.is_staff):
        messages.error(request, "This quiz is not yet available.")
        return redirect('courses:course_detail', course_slug=course_slug)
    
    # Check if the student has already attempted the quiz
    attempt = QuizAttempt.objects.filter(enrollment=enrollment, quiz=quiz).first()
    
    context = {
        'course': course,
        'module': module,
        'quiz': quiz,
        'attempt': attempt,
    }
    
    return render(request, 'courses/quiz/quiz_detail.html', context)

@login_required
def take_quiz(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if the user is enrolled
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
    except Enrollment.DoesNotExist:
        messages.error(request, "You must be enrolled in this course to take quizzes.")
        return redirect('courses:course_detail', course_slug=course_slug)
    
    # Get the quiz or return 404
    try:
        quiz = module.quiz
    except Quiz.DoesNotExist:
        messages.error(request, f"No quiz exists for module '{module.title}'.")
        return redirect('courses:course_detail', course_slug=course_slug)
    
    # Check if the quiz is published
    if not quiz.is_published and not (course.instructor_user == request.user or request.user.is_staff):
        messages.error(request, "This quiz is not yet available.")
        return redirect('courses:course_detail', course_slug=course_slug)
    
    # Check if the student has already completed the quiz
    existing_attempt = QuizAttempt.objects.filter(
        enrollment=enrollment, 
        quiz=quiz,
        completed_at__isnull=False
    ).first()
    
    if existing_attempt:
        messages.info(request, "You have already completed this quiz. You can view your results.")
        return redirect('courses:quiz_results', course_slug=course_slug, module_id=module_id, attempt_id=existing_attempt.id)
    
    # Get or create a quiz attempt
    attempt, created = QuizAttempt.objects.get_or_create(
        enrollment=enrollment,
        quiz=quiz,
        defaults={'started_at': timezone.now()}
    )
    
    # If not created, update the started_at time if not completed
    if not created and not attempt.completed_at:
        attempt.started_at = timezone.now()
        attempt.save()
    
    if request.method == 'POST':
        form = QuizResponseForm(request.POST, quiz=quiz)
        if form.is_valid():
            with transaction.atomic():
                # Mark the attempt as completed
                attempt.completed_at = timezone.now()
                
                # Process each question response
                for question in quiz.questions.all():
                    field_name = f'question_{question.id}'
                    if field_name in form.cleaned_data:
                        choice_id = form.cleaned_data[field_name]
                        choice = get_object_or_404(Choice, id=choice_id)
                        
                        # Create or update the response
                        QuizResponse.objects.update_or_create(
                            attempt=attempt,
                            question=question,
                            defaults={'selected_choice': choice}
                        )
                
                # Calculate the score and save the attempt
                attempt.save()  # This will trigger the score calculation in the save method
                
                messages.success(request, "Quiz completed successfully! Here are your results.")
                return redirect('courses:quiz_results', course_slug=course_slug, module_id=module_id, attempt_id=attempt.id)
    else:
        form = QuizResponseForm(quiz=quiz)
    
    context = {
        'course': course,
        'module': module,
        'quiz': quiz,
        'form': form,
        'attempt': attempt,
    }
    
    return render(request, 'courses/quiz/take_quiz.html', context)

@login_required
def quiz_results(request, course_slug, module_id, attempt_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Get the quiz or return 404
    try:
        quiz = module.quiz
    except Quiz.DoesNotExist:
        messages.error(request, f"No quiz exists for module '{module.title}'.")
        return redirect('courses:course_detail', course_slug=course_slug)
    
    # Get the attempt or return 404
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, quiz=quiz)
    
    # Check if the user is the one who took the quiz or is the instructor
    is_instructor = course.instructor_user == request.user
    if attempt.enrollment.user != request.user and not (is_instructor or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to view these quiz results.")
    
    # Get all responses for this attempt
    responses = attempt.responses.all().select_related('question', 'selected_choice')
    
    # Organize responses by question
    questions_data = []
    for question in quiz.questions.all():
        response = next((r for r in responses if r.question_id == question.id), None)
        correct_choice = question.get_correct_choice()
        
        questions_data.append({
            'question': question,
            'response': response,
            'is_correct': response and response.is_correct(),
            'correct_choice': correct_choice,
        })
    
    context = {
        'course': course,
        'module': module,
        'quiz': quiz,
        'attempt': attempt,
        'questions_data': questions_data,
        'is_instructor': is_instructor,
    }
    
    return render(request, 'courses/quiz/quiz_results.html', context)


