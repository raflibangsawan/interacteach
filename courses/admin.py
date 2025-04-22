from django.contrib import admin
from .models import (
    Course, Module, Lesson, Enrollment, LessonProgress, InstructorProfile, 
    ForumThread, ForumReply, Quiz, Question, Choice, QuizAttempt, QuizResponse
)

# Custom admin actions
def mark_as_completed(modeladmin, request, queryset):
    queryset.update(completed=True)
mark_as_completed.short_description = "Mark selected items as completed"

def mark_as_not_completed(modeladmin, request, queryset):
    queryset.update(completed=False)
mark_as_not_completed.short_description = "Mark selected items as not completed"

def publish_courses(modeladmin, request, queryset):
    queryset.update(is_published=True)
publish_courses.short_description = "Publish selected courses"

def unpublish_courses(modeladmin, request, queryset):
    queryset.update(is_published=False)
unpublish_courses.short_description = "Unpublish selected courses"

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'instructor_user', 'duration', 'is_published', 'total_modules', 'total_lessons', 'total_enrollments', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description', 'instructor')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
    date_hierarchy = 'created_at'
    readonly_fields = ('total_modules', 'total_lessons', 'total_enrollments')
    actions = [publish_courses, unpublish_courses]
    
    def total_modules(self, obj):
        return obj.total_modules()
    total_modules.short_description = 'Modules'
    
    def total_lessons(self, obj):
        return obj.total_lessons()
    total_lessons.short_description = 'Lessons'
    
    def total_enrollments(self, obj):
        return obj.total_enrollments()
    total_enrollments.short_description = 'Enrollments'

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'total_lessons', 'has_quiz')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    inlines = [LessonInline]
    ordering = ('course', 'order')
    
    def total_lessons(self, obj):
        return obj.total_lessons()
    total_lessons.short_description = 'Lessons'
    
    def has_quiz(self, obj):
        return hasattr(obj, 'quiz')
    has_quiz.boolean = True
    has_quiz.short_description = 'Has Quiz'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order')
    list_filter = ('module__course', 'module')
    search_fields = ('title', 'content')
    ordering = ('module', 'order')

class LessonProgressInline(admin.TabularInline):
    model = LessonProgress
    extra = 1
    readonly_fields = ('last_accessed',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'completed', 'progress')
    list_filter = ('completed', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
    date_hierarchy = 'enrolled_at'
    inlines = [LessonProgressInline]
    actions = [mark_as_completed, mark_as_not_completed]
    
    def progress(self, obj):
        return f"{obj.progress_percentage()}%"
    progress.short_description = 'Progress'

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'completed', 'last_accessed')
    list_filter = ('completed', 'last_accessed')
    search_fields = ('enrollment__user__username', 'lesson__title')
    date_hierarchy = 'last_accessed'
    actions = [mark_as_completed, mark_as_not_completed]

@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'expertise', 'courses_count')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'expertise')
    raw_id_fields = ('user',)

# Forum admin
class ForumReplyInline(admin.TabularInline):
    model = ForumReply
    extra = 1
    readonly_fields = ('created_at',)

@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'user', 'created_at', 'is_pinned', 'is_locked', 'replies_count')
    list_filter = ('is_pinned', 'is_locked', 'created_at', 'course')
    search_fields = ('title', 'content', 'user__username')
    date_hierarchy = 'created_at'
    inlines = [ForumReplyInline]
    
    def replies_count(self, obj):
        return obj.replies.count()
    replies_count.short_description = 'Replies'

@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ('thread', 'user', 'created_at', 'is_solution')
    list_filter = ('is_solution', 'created_at')
    search_fields = ('content', 'user__username', 'thread__title')
    date_hierarchy = 'created_at'

# Quiz admin
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    max_num = 4

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    inlines = [ChoiceInline]

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'is_published', 'passing_score', 'time_limit', 'total_questions', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description', 'module__title', 'module__course__title')
    date_hierarchy = 'created_at'
    
    def total_questions(self, obj):
        return obj.total_questions()
    total_questions.short_description = 'Questions'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'points', 'order')
    list_filter = ('quiz',)
    search_fields = ('text', 'quiz__title')
    inlines = [ChoiceInline]
    ordering = ('quiz', 'order')

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct', 'order')
    list_filter = ('is_correct', 'question__quiz')
    search_fields = ('text', 'question__text')
    ordering = ('question', 'order')

class QuizResponseInline(admin.TabularInline):
    model = QuizResponse
    extra = 0
    readonly_fields = ('question', 'selected_choice', 'is_correct')
    
    def is_correct(self, obj):
        return obj.is_correct()
    is_correct.boolean = True
    is_correct.short_description = 'Correct'

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'quiz', 'started_at', 'completed_at', 'score', 'passed')
    list_filter = ('passed', 'started_at', 'completed_at', 'quiz')
    search_fields = ('enrollment__user__username', 'quiz__title')
    date_hierarchy = 'started_at'
    inlines = [QuizResponseInline]
    readonly_fields = ('score', 'passed')

@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_choice', 'is_correct')
    list_filter = ('attempt__quiz',)
    search_fields = ('attempt__enrollment__user__username', 'question__text')
    
    def is_correct(self, obj):
        return obj.is_correct()
    is_correct.boolean = True
    is_correct.short_description = 'Correct'
