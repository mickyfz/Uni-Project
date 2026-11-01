from django.db import models
from django.conf import settings

class Semester(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="e.g. Spring 2026, Fall 2026")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True, help_text="e.g. CSE-301")
    title = models.CharField(max_length=150, help_text="e.g. Data Structures and Algorithms")
    description = models.TextField(blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='courses')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='taught_courses'
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        limit_choices_to={'role': 'student'},
        related_name='enrolled_courses'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.title}"
