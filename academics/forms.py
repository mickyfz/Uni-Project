from django import forms
from .models import Course, Semester
from core.models import CustomUser

class CourseForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role=CustomUser.ROLE_STUDENT),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'})
    )

    class Meta:
        model = Course
        fields = ['code', 'title', 'semester', 'description', 'students']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CSE-311'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Database Systems'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Course overview and syllabus...'}),
        }
