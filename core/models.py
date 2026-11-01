from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_STUDENT = 'student'
    ROLE_TEACHER = 'teacher'
    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_TEACHER, 'Teacher'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    university_id = models.CharField(max_length=30, blank=True, null=True, help_text="Student ID or Faculty ID")
    department = models.CharField(max_length=100, default='Computer Science & Engineering', blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    @property
    def is_teacher(self):
        return self.role == self.ROLE_TEACHER

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
