from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    instructor = models.CharField(max_length=100)
    instructor_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_courses'
    )
    image = models.CharField(max_length=200, default='/static/courses/images/course-placeholder.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.CharField(max_length=50, default="4 weeks")
    is_published = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('courses:course_detail', kwargs={'course_slug': self.slug})
    
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
    
    def has_quiz(self):
        return hasattr(self, 'quiz')

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
        return reverse('courses:lesson_detail', kwargs={
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

class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    bio = models.TextField(blank=True)
    expertise = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    profile_image = models.CharField(max_length=200, default='https://img.freepik.com/free-vector/blue-circle-with-white-user_78370-4707.jpg?t=st=1746949129~exp=1746952729~hmac=2e139c08af0e5fb473952938f8e689336a8a643d2df0fd1310d8d571ba8872ee&w=740')
    
    def __str__(self):
        return f"Instructor: {self.user.get_full_name() or self.user.username}"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def courses_count(self):
        return Course.objects.filter(instructor_user=self.user).count()


class ForumThread(models.Model):
    course = models.ForeignKey(Course, related_name='forum_threads', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='forum_threads', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('courses:forum_thread_detail', kwargs={
            'course_slug': self.course.slug,
            'thread_id': self.id
        })
    
    def replies_count(self):
        return self.replies.count()
    
    def last_activity(self):
        last_reply = self.replies.order_by('-created_at').first()
        if last_reply:
            return last_reply.created_at
        return self.created_at

class ForumReply(models.Model):
    thread = models.ForeignKey(ForumThread, related_name='replies', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='forum_replies', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_solution = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='child_replies', on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Forum replies'
    
    def __str__(self):
        return f'Reply by {self.user.username} on {self.thread.title}'
    
    @property
    def is_parent(self):
        return self.parent is None
    
    @property
    def has_children(self):
        return self.child_replies.exists()


# Quiz models
class Quiz(models.Model):
    module = models.OneToOneField(Module, related_name='quiz', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_limit = models.PositiveIntegerField(default=0, help_text="Time limit in minutes (0 for no limit)")
    passing_score = models.PositiveIntegerField(default=70, help_text="Passing score percentage")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Quizzes'
    
    def __str__(self):
        return f"Quiz: {self.title}"
    
    def get_absolute_url(self):
        return reverse('courses:quiz_detail', kwargs={
            'course_slug': self.module.course.slug,
            'module_id': self.module.id
        })
    
    def total_questions(self):
        return self.questions.count()
    
    def total_points(self):
        return sum(question.points for question in self.questions.all())

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    # Fix: Provide a default value for created_at
    created_at = models.DateTimeField(default=timezone.now)
    # Fix: Change auto_now_add to auto_now for updated_at
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Question {self.order}: {self.text[:50]}..."
    
    def get_correct_choice(self):
        return self.choices.filter(is_correct=True).first()

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Choice: {self.text[:50]}..."

class QuizAttempt(models.Model):
    enrollment = models.ForeignKey(Enrollment, related_name='quiz_attempts', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name='attempts', on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    passed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = [['enrollment', 'quiz']]
    
    def __str__(self):
        return f"{self.enrollment.user.username}'s attempt at {self.quiz.title}"
    
    def calculate_score(self):
        if not self.completed_at:
            return 0
        
        total_points = self.quiz.total_points()
        if total_points == 0:
            return 0
        
        earned_points = 0
        for response in self.responses.all():
            if response.selected_choice and response.selected_choice.is_correct:
                earned_points += response.question.points
        
        return (earned_points / total_points) * 100
    
    def is_passed(self):
        return self.score >= self.quiz.passing_score if self.score is not None else False
    
    def save(self, *args, **kwargs):
        if self.completed_at and self.score is None:
            self.score = self.calculate_score()
            self.passed = self.is_passed()
        super().save(*args, **kwargs)

class QuizResponse(models.Model):
    attempt = models.ForeignKey(QuizAttempt, related_name='responses', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        unique_together = [['attempt', 'question']]
    
    def __str__(self):
        return f"Response to {self.question}"
    
    def is_correct(self):
        if not self.selected_choice:
            return False
        return self.selected_choice.is_correct
