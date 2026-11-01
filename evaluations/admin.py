from django.contrib import admin
from .models import Quiz, QuizQuestion, QuizChoice, QuizSubmission, QuizAnswer, VivaAssessment, VivaSubmission

class QuizChoiceInline(admin.TabularInline):
    model = QuizChoice
    extra = 4

class QuizQuestionInline(admin.StackedInline):
    model = QuizQuestion
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'term', 'total_marks', 'duration_minutes', 'is_published', 'created_at')
    list_filter = ('term', 'course', 'is_published')
    search_fields = ('title', 'course__title', 'course__code')

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz', 'question_type', 'marks', 'order')
    list_filter = ('quiz__course', 'quiz__term', 'question_type')
    inlines = [QuizChoiceInline]

class QuizAnswerInline(admin.TabularInline):
    model = QuizAnswer
    extra = 0
    readonly_fields = ('question', 'selected_choice', 'text_response')

@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'obtained_marks', 'is_graded', 'submitted_at')
    list_filter = ('is_graded', 'quiz__term', 'quiz__course')
    search_fields = ('student__username', 'student__university_id', 'quiz__title')
    inlines = [QuizAnswerInline]

@admin.register(VivaAssessment)
class VivaAssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'term', 'total_marks', 'due_date', 'is_published', 'created_at')
    list_filter = ('term', 'course', 'is_published')
    search_fields = ('title', 'course__title', 'course__code')

@admin.register(VivaSubmission)
class VivaSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'viva', 'obtained_marks', 'is_graded', 'submitted_at')
    list_filter = ('is_graded', 'viva__term', 'viva__course')
    search_fields = ('student__username', 'student__university_id', 'viva__title')
