from django import forms
from .models import Quiz, QuizQuestion, QuizChoice, VivaAssessment, VivaSubmission, QuizSubmission

class QuizForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )

    class Meta:
        model = Quiz
        fields = ['course', 'term', 'title', 'instructions', 'total_marks', 'duration_minutes', 'due_date', 'is_published']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'term': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Midterm Quiz: Database Normalization'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Instructions for students...'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['course'].queryset = teacher.taught_courses.all()

class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['question_text', 'question_type', 'marks', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter question here...'}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class VivaAssessmentForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )

    class Meta:
        model = VivaAssessment
        fields = ['course', 'term', 'title', 'description', 'total_marks', 'due_date', 'is_published']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'term': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Midterm Viva: Project Presentation'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Provide topics/questions students must answer in their video...'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['course'].queryset = teacher.taught_courses.all()

class VivaSubmissionForm(forms.ModelForm):
    class Meta:
        model = VivaSubmission
        fields = ['video_file', 'notes']
        widgets = {
            'video_file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'video/*'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional: Add summary notes or question timestamps...'}),
        }

class GradeVivaForm(forms.ModelForm):
    class Meta:
        model = VivaSubmission
        fields = ['obtained_marks', 'teacher_feedback']
        widgets = {
            'obtained_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'teacher_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Feedback on viva presentation, pronunciation, answers...'}),
        }

class GradeQuizForm(forms.ModelForm):
    class Meta:
        model = QuizSubmission
        fields = ['obtained_marks', 'teacher_feedback']
        widgets = {
            'obtained_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'teacher_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Teacher feedback on quiz performance...'}),
        }
