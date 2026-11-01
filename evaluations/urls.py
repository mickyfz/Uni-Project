from django.urls import path
from . import views

urlpatterns = [
    # Teacher endpoints
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/courses/<int:course_id>/', views.teacher_course_detail, name='teacher_course_detail'),
    path('teacher/courses/<int:course_id>/gradesheet/', views.course_grade_sheet, name='course_grade_sheet'),
    
    path('quizzes/create/', views.create_quiz, name='create_quiz'),
    path('courses/<int:course_id>/quizzes/create/', views.create_quiz, name='course_create_quiz'),
    path('quizzes/<int:quiz_id>/questions/', views.quiz_manage_questions, name='quiz_manage_questions'),
    path('quizzes/<int:quiz_id>/submissions/', views.quiz_submissions_list, name='quiz_submissions_list'),
    path('submissions/quiz/<int:submission_id>/grade/', views.grade_quiz_submission, name='grade_quiz_submission'),

    path('vivas/create/', views.create_viva, name='create_viva'),
    path('courses/<int:course_id>/vivas/create/', views.create_viva, name='course_create_viva'),
    path('vivas/<int:viva_id>/submissions/', views.viva_submissions_list, name='viva_submissions_list'),
    path('submissions/viva/<int:submission_id>/grade/', views.grade_viva_submission, name='grade_viva_submission'),

    # Student endpoints
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/courses/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    path('student/grades/', views.student_grade_report, name='student_grade_report'),
    
    path('quizzes/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('vivas/<int:viva_id>/submit/', views.submit_viva, name='submit_viva'),
]
