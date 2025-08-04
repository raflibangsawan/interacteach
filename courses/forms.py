from django import forms
from .models import Course, Module, Lesson, InstructorProfile, ForumThread, ForumReply, Quiz, Question, Choice

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
        fields = ['title', 'content', 'video_url', 'meeting_link', 'order']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'meeting_link': forms.URLInput(attrs={'placeholder': 'https://meet.google.com/... or https://zoom.us/...'}),
        }

class InstructorProfileForm(forms.ModelForm):
    class Meta:
        model = InstructorProfile
        fields = ['bio', 'expertise', 'website', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

# Forum forms
class ForumThreadForm(forms.ModelForm):
    class Meta:
        model = ForumThread
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Thread title'}),
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 6, 'placeholder': 'Share your thoughts, questions, or insights...'}),
        }

class ForumReplyForm(forms.ModelForm):
    class Meta:
        model = ForumReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Write your reply...'}),
        }
        labels = {
            'content': '',
        }

class NestedReplyForm(forms.ModelForm):
    class Meta:
        model = ForumReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-input nested-reply-textarea', 'rows': 3, 'placeholder': 'Write your reply...'}),
        }
        labels = {
            'content': '',
        }

# Quiz forms
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'time_limit', 'passing_score', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Quiz title'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Quiz description'}),
            'time_limit': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'max': 100}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'points', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Question text'}),
            'points': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'order': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct', 'order']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Choice text'}),
            'order': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
        }

# Formset for creating multiple choices at once
ChoiceFormSet = forms.inlineformset_factory(
    Question, 
    Choice,
    form=ChoiceForm,
    extra=4,
    max_num=4,
    min_num=4,
    validate_min=True,
    validate_max=True,
    can_delete=False
)

# Form for taking a quiz
class QuizResponseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        quiz = kwargs.pop('quiz')
        super().__init__(*args, **kwargs)
        
        for question in quiz.questions.all():
            choices = [(choice.id, choice.text) for choice in question.choices.all()]
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=question.text,
                required=True
            )
