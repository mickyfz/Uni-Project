from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class StudentTeacherRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    university_id = forms.CharField(
        max_length=30,
        required=True,
        label="Student ID / Faculty ID",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. STU-2026-001 or FAC-102'})
    )
    department = forms.CharField(
        max_length=100,
        required=True,
        initial='Computer Science & Engineering',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Computer Science & Engineering'})
    )
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'university_id', 'department', 'phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['role'].widget.attrs['class'] = 'form-select'

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
