from django.contrib import admin
from .models import Semester, Course

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_editable = ('is_active',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'semester', 'teacher')
    list_filter = ('semester', 'teacher')
    search_fields = ('code', 'title')
    filter_horizontal = ('students',)
