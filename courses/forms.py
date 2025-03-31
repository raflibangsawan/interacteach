from django import forms
from .models import Course, Module, Lesson, InstructorProfile

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'image', 'duration', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video_url', 'order']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

class InstructorProfileForm(forms.ModelForm):
    class Meta:
        model = InstructorProfile
        fields = ['bio', 'expertise', 'website', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

