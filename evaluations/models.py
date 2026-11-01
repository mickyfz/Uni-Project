from django.db import models
from django.conf import settings
from academics.models import Course

class TermChoices(models.TextChoices):
    MIDTERM = 'midterm', 'Midterm'
    FINAL = 'final', 'Final'


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    term = models.CharField(max_length=10, choices=TermChoices.choices, default=TermChoices.MIDTERM)
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    total_marks = models.PositiveIntegerField(default=20)
    duration_minutes = models.PositiveIntegerField(default=30)
    due_date = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_term_display()}] {self.course.code}: {self.title}"


class QuestionType(models.TextChoices):
    MCQ = 'mcq', 'Multiple Choice'
    SHORT_ANSWER = 'short_answer', 'Short Answer / Descriptive'


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QuestionType.choices, default=QuestionType.MCQ)
    marks = models.PositiveIntegerField(default=5)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"


class QuizChoice(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.choice_text} ({'Correct' if self.is_correct else 'Wrong'})"


class QuizSubmission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='quiz_submissions'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    obtained_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    is_graded = models.BooleanField(default=False)
    teacher_feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('quiz', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.obtained_marks}/{self.quiz.total_marks})"


class QuizAnswer(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(QuizChoice, on_delete=models.SET_NULL, null=True, blank=True)
    text_response = models.TextField(blank=True)
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Ans for {self.question.id} by {self.submission.student.username}"


class VivaAssessment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='vivas')
    term = models.CharField(max_length=10, choices=TermChoices.choices, default=TermChoices.MIDTERM)
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Topics, questions, or guidelines students must address in their video")
    total_marks = models.PositiveIntegerField(default=30)
    due_date = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_term_display()}] {self.course.code}: {self.title}"


class VivaSubmission(models.Model):
    viva = models.ForeignKey(VivaAssessment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='viva_submissions'
    )
    video_file = models.FileField(upload_to='viva_videos/', help_text="Upload your viva answer video (mp4, webm, avi, mov)")
    notes = models.TextField(blank=True, help_text="Notes, summary or topic timestamps for the teacher")
    submitted_at = models.DateTimeField(auto_now_add=True)
    obtained_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_graded = models.BooleanField(default=False)
    teacher_feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('viva', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} - {self.viva.title} ({'Graded: ' + str(self.obtained_marks) if self.is_graded else 'Pending'})"
