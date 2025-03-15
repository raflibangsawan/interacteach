from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    instructor = models.CharField(max_length=100)
    image = models.CharField(max_length=200, default='/static/images/course-placeholder.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.CharField(max_length=50, default="4 weeks")
    level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], default='beginner')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'course_slug': self.slug})
    
    def total_modules(self):
        return self.modules.count()
    
    def total_lessons(self):
        return Lesson.objects.filter(module__course=self).count()
    
    def total_enrollments(self):
        return self.enrollments.count()
    
    class Meta:
        ordering = ['-created_at']

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f'{self.order}. {self.title}'
    
    def total_lessons(self):
        return self.lessons.count()

class Lesson(models.Model):
    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('lesson_detail', kwargs={
            'course_slug': self.module.course.slug,
            'lesson_id': self.id
        })

class Enrollment(models.Model):
    user = models.ForeignKey(User, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = [['user', 'course']]
    
    def __str__(self):
        return f'{self.user.username} enrolled in {self.course.title}'
    
    def progress_percentage(self):
        total_lessons = Lesson.objects.filter(module__course=self.course).count()
        if total_lessons == 0:
            return 0
        
        completed_lessons = LessonProgress.objects.filter(
            enrollment=self, 
            completed=True
        ).count()
        
        return int((completed_lessons / total_lessons) * 100)

class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, related_name='progress', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['enrollment', 'lesson']]
    
    def __str__(self):
        return f'{self.enrollment.user.username} - {self.lesson.title} - {"Completed" if self.completed else "In Progress"}'

