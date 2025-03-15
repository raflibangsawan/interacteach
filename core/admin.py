from django.contrib import admin
from .models import Course, Module, Lesson, Enrollment, LessonProgress

# Custom admin actions
def mark_as_completed(modeladmin, request, queryset):
    queryset.update(completed=True)
mark_as_completed.short_description = "Mark selected items as completed"

def mark_as_not_completed(modeladmin, request, queryset):
    queryset.update(completed=False)
mark_as_not_completed.short_description = "Mark selected items as not completed"

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'level', 'duration', 'total_modules', 'total_lessons', 'total_enrollments', 'created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('title', 'description', 'instructor')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
    date_hierarchy = 'created_at'
    readonly_fields = ('total_modules', 'total_lessons', 'total_enrollments')
    
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
    list_display = ('title', 'course', 'order', 'total_lessons')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    inlines = [LessonInline]
    ordering = ('course', 'order')
    
    def total_lessons(self, obj):
        return obj.total_lessons()
    total_lessons.short_description = 'Lessons'

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

