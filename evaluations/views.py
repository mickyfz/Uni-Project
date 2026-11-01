from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q

from academics.models import Course, Semester
from core.models import CustomUser
from .models import (
    Quiz, QuizQuestion, QuizChoice, QuizSubmission, QuizAnswer,
    VivaAssessment, VivaSubmission, TermChoices
)
from .forms import (
    QuizForm, QuizQuestionForm, VivaAssessmentForm, VivaSubmissionForm,
    GradeVivaForm, GradeQuizForm
)

# ----------------- TEACHER VIEWS -----------------

@login_required
def teacher_dashboard(request):
    if not (request.user.is_teacher or request.user.is_staff):
        return redirect('student_dashboard')

    courses = Course.objects.filter(teacher=request.user)
    quizzes = Quiz.objects.filter(course__in=courses).order_by('-created_at')
    vivas = VivaAssessment.objects.filter(course__in=courses).order_by('-created_at')

    # Submissions needing grading
    pending_quizzes = QuizSubmission.objects.filter(quiz__in=quizzes, is_graded=False)
    pending_vivas = VivaSubmission.objects.filter(viva__in=vivas, is_graded=False)

    context = {
        'courses': courses,
        'quizzes': quizzes,
        'vivas': vivas,
        'pending_quizzes': pending_quizzes,
        'pending_vivas': pending_vivas,
    }
    return render(request, 'evaluations/teacher_dashboard.html', context)


@login_required
def teacher_course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    
    midterm_quizzes = Quiz.objects.filter(course=course, term=TermChoices.MIDTERM)
    midterm_vivas = VivaAssessment.objects.filter(course=course, term=TermChoices.MIDTERM)
    
    final_quizzes = Quiz.objects.filter(course=course, term=TermChoices.FINAL)
    final_vivas = VivaAssessment.objects.filter(course=course, term=TermChoices.FINAL)

    students = course.students.all()

    context = {
        'course': course,
        'midterm_quizzes': midterm_quizzes,
        'midterm_vivas': midterm_vivas,
        'final_quizzes': final_quizzes,
        'final_vivas': final_vivas,
        'students': students,
    }
    return render(request, 'evaluations/teacher_course_detail.html', context)


@login_required
def create_quiz(request, course_id=None):
    if not (request.user.is_teacher or request.user.is_staff):
        messages.error(request, "Access restricted to teachers.")
        return redirect('dashboard')

    initial_course = None
    if course_id:
        initial_course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == 'POST':
        form = QuizForm(request.POST, teacher=request.user)
        if form.is_valid():
            quiz = form.save()
            messages.success(request, f"Quiz '{quiz.title}' created! Now add questions.")
            return redirect('quiz_manage_questions', quiz_id=quiz.id)
    else:
        form = QuizForm(teacher=request.user, initial={'course': initial_course})

    return render(request, 'evaluations/quiz_form.html', {'form': form, 'course': initial_course})


@login_required
def quiz_manage_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course__teacher=request.user)
    questions = quiz.questions.prefetch_related('choices').all()

    if request.method == 'POST':
        if 'add_question' in request.POST:
            q_form = QuizQuestionForm(request.POST)
            if q_form.is_valid():
                new_q = q_form.save(commit=False)
                new_q.quiz = quiz
                new_q.save()

                # If MCQ, process choices from dynamic inputs
                if new_q.question_type == 'mcq':
                    choice_texts = request.POST.getlist('choice_text')
                    correct_idx = request.POST.get('correct_choice')
                    for idx, c_text in enumerate(choice_texts):
                        c_text = c_text.strip()
                        if c_text:
                            is_correct = (str(idx) == str(correct_idx))
                            QuizChoice.objects.create(question=new_q, choice_text=c_text, is_correct=is_correct)

                messages.success(request, "Question added successfully.")
                return redirect('quiz_manage_questions', quiz_id=quiz.id)
        
        elif 'delete_question' in request.POST:
            q_id = request.POST.get('question_id')
            q = get_object_or_404(QuizQuestion, id=q_id, quiz=quiz)
            q.delete()
            messages.info(request, "Question removed.")
            return redirect('quiz_manage_questions', quiz_id=quiz.id)

    q_form = QuizQuestionForm()
    return render(request, 'evaluations/quiz_manage_questions.html', {
        'quiz': quiz,
        'questions': questions,
        'q_form': q_form,
    })


@login_required
def create_viva(request, course_id=None):
    if not (request.user.is_teacher or request.user.is_staff):
        messages.error(request, "Access restricted to teachers.")
        return redirect('dashboard')

    initial_course = None
    if course_id:
        initial_course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == 'POST':
        form = VivaAssessmentForm(request.POST, teacher=request.user)
        if form.is_valid():
            viva = form.save()
            messages.success(request, f"Viva Assessment '{viva.title}' created.")
            return redirect('teacher_course_detail', course_id=viva.course.id)
    else:
        form = VivaAssessmentForm(teacher=request.user, initial={'course': initial_course})

    return render(request, 'evaluations/viva_form.html', {'form': form, 'course': initial_course})


@login_required
def quiz_submissions_list(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course__teacher=request.user)
    submissions = quiz.submissions.select_related('student').all()
    return render(request, 'evaluations/quiz_submissions_list.html', {
        'quiz': quiz,
        'submissions': submissions
    })


@login_required
def grade_quiz_submission(request, submission_id):
    submission = get_object_or_404(QuizSubmission, id=submission_id, quiz__course__teacher=request.user)
    answers = submission.answers.select_related('question', 'selected_choice').all()

    if request.method == 'POST':
        form = GradeQuizForm(request.POST, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.is_graded = True
            sub.save()
            messages.success(request, f"Marks and feedback saved for student {sub.student.get_full_name() or sub.student.username}.")
            return redirect('quiz_submissions_list', quiz_id=submission.quiz.id)
    else:
        form = GradeQuizForm(instance=submission)

    return render(request, 'evaluations/grade_quiz.html', {
        'submission': submission,
        'answers': answers,
        'form': form,
    })


@login_required
def viva_submissions_list(request, viva_id):
    viva = get_object_or_404(VivaAssessment, id=viva_id, course__teacher=request.user)
    submissions = viva.submissions.select_related('student').all()
    return render(request, 'evaluations/viva_submissions_list.html', {
        'viva': viva,
        'submissions': submissions
    })


@login_required
def grade_viva_submission(request, submission_id):
    submission = get_object_or_404(VivaSubmission, id=submission_id, viva__course__teacher=request.user)

    if request.method == 'POST':
        form = GradeVivaForm(request.POST, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.is_graded = True
            sub.graded_at = timezone.now()
            sub.save()
            messages.success(request, f"Viva graded successfully for student {sub.student.get_full_name() or sub.student.username}!")
            return redirect('viva_submissions_list', viva_id=submission.viva.id)
    else:
        form = GradeVivaForm(instance=submission)

    return render(request, 'evaluations/grade_viva.html', {
        'submission': submission,
        'form': form
    })


@login_required
def course_grade_sheet(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    students = course.students.all().order_by('university_id', 'username')

    # All quizzes and vivas for this course
    midterm_quizzes = Quiz.objects.filter(course=course, term=TermChoices.MIDTERM)
    midterm_vivas = VivaAssessment.objects.filter(course=course, term=TermChoices.MIDTERM)
    final_quizzes = Quiz.objects.filter(course=course, term=TermChoices.FINAL)
    final_vivas = VivaAssessment.objects.filter(course=course, term=TermChoices.FINAL)

    # Compute breakdown for each student
    student_records = []
    for student in students:
        # Midterm Quiz
        mid_q_sub = QuizSubmission.objects.filter(quiz__in=midterm_quizzes, student=student)
        mid_q_obtained = sum([float(s.obtained_marks) for s in mid_q_sub])
        mid_q_total = sum([q.total_marks for q in midterm_quizzes])

        # Midterm Viva
        mid_v_sub = VivaSubmission.objects.filter(viva__in=midterm_vivas, student=student, is_graded=True)
        mid_v_obtained = sum([float(s.obtained_marks or 0) for s in mid_v_sub])
        mid_v_total = sum([v.total_marks for v in midterm_vivas])

        # Final Quiz
        fin_q_sub = QuizSubmission.objects.filter(quiz__in=final_quizzes, student=student)
        fin_q_obtained = sum([float(s.obtained_marks) for s in fin_q_sub])
        fin_q_total = sum([q.total_marks for q in final_quizzes])

        # Final Viva
        fin_v_sub = VivaSubmission.objects.filter(viva__in=final_vivas, student=student, is_graded=True)
        fin_v_obtained = sum([float(s.obtained_marks or 0) for s in fin_v_sub])
        fin_v_total = sum([v.total_marks for v in final_vivas])

        total_obtained = mid_q_obtained + mid_v_obtained + fin_q_obtained + fin_v_obtained
        grand_total = mid_q_total + mid_v_total + fin_q_total + fin_v_total
        percentage = round((total_obtained / grand_total * 100), 1) if grand_total > 0 else 0

        # Grade calculation
        if percentage >= 80:
            grade = 'A+'
        elif percentage >= 75:
            grade = 'A'
        elif percentage >= 70:
            grade = 'A-'
        elif percentage >= 65:
            grade = 'B+'
        elif percentage >= 60:
            grade = 'B'
        elif percentage >= 50:
            grade = 'C'
        elif percentage >= 40:
            grade = 'D'
        else:
            grade = 'F'

        student_records.append({
            'student': student,
            'mid_q_obtained': mid_q_obtained,
            'mid_q_total': mid_q_total,
            'mid_v_obtained': mid_v_obtained,
            'mid_v_total': mid_v_total,
            'mid_total': mid_q_obtained + mid_v_obtained,
            'fin_q_obtained': fin_q_obtained,
            'fin_q_total': fin_q_total,
            'fin_v_obtained': fin_v_obtained,
            'fin_v_total': fin_v_total,
            'fin_total': fin_q_obtained + fin_v_obtained,
            'total_obtained': total_obtained,
            'grand_total': grand_total,
            'percentage': percentage,
            'grade': grade,
        })

    return render(request, 'evaluations/course_grade_sheet.html', {
        'course': course,
        'student_records': student_records,
    })


# ----------------- STUDENT VIEWS -----------------

@login_required
def student_dashboard(request):
    if request.user.is_teacher:
        return redirect('teacher_dashboard')

    courses = request.user.enrolled_courses.select_related('semester', 'teacher').all()

    # Active Quizzes & Vivas for enrolled courses
    quizzes = Quiz.objects.filter(course__in=courses, is_published=True).order_by('-created_at')
    vivas = VivaAssessment.objects.filter(course__in=courses, is_published=True).order_by('-created_at')

    # Student's submissions
    my_quiz_subs = {s.quiz_id: s for s in QuizSubmission.objects.filter(student=request.user)}
    my_viva_subs = {s.viva_id: s for s in VivaSubmission.objects.filter(student=request.user)}

    # Attach submission status
    quiz_items = []
    for q in quizzes:
        sub = my_quiz_subs.get(q.id)
        quiz_items.append({'quiz': q, 'submission': sub})

    viva_items = []
    for v in vivas:
        sub = my_viva_subs.get(v.id)
        viva_items.append({'viva': v, 'submission': sub})

    context = {
        'courses': courses,
        'quiz_items': quiz_items,
        'viva_items': viva_items,
    }
    return render(request, 'evaluations/student_dashboard.html', context)


@login_required
def student_course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, students=request.user)

    midterm_quizzes = Quiz.objects.filter(course=course, term=TermChoices.MIDTERM, is_published=True)
    midterm_vivas = VivaAssessment.objects.filter(course=course, term=TermChoices.MIDTERM, is_published=True)

    final_quizzes = Quiz.objects.filter(course=course, term=TermChoices.FINAL, is_published=True)
    final_vivas = VivaAssessment.objects.filter(course=course, term=TermChoices.FINAL, is_published=True)

    my_quiz_subs = {s.quiz_id: s for s in QuizSubmission.objects.filter(student=request.user)}
    my_viva_subs = {s.viva_id: s for s in VivaSubmission.objects.filter(student=request.user)}

    def build_items(qs, sub_map):
        return [{'item': obj, 'sub': sub_map.get(obj.id)} for obj in qs]

    context = {
        'course': course,
        'mid_quizzes': build_items(midterm_quizzes, my_quiz_subs),
        'mid_vivas': build_items(midterm_vivas, my_viva_subs),
        'fin_quizzes': build_items(final_quizzes, my_quiz_subs),
        'fin_vivas': build_items(final_vivas, my_viva_subs),
    }
    return render(request, 'evaluations/student_course_detail.html', context)


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_published=True)
    
    # Check course enrollment
    if not quiz.course.students.filter(id=request.user.id).exists():
        messages.error(request, "You are not enrolled in this course.")
        return redirect('student_dashboard')

    # Check if already submitted
    existing_sub = QuizSubmission.objects.filter(quiz=quiz, student=request.user).first()
    if existing_sub:
        messages.info(request, "You have already submitted this quiz.")
        return render(request, 'evaluations/quiz_result.html', {'quiz': quiz, 'submission': existing_sub})

    questions = quiz.questions.prefetch_related('choices').all()

    if request.method == 'POST':
        # Create submission
        submission = QuizSubmission.objects.create(quiz=quiz, student=request.user)
        total_score = 0.0
        has_descriptive = False

        for question in questions:
            if question.question_type == 'mcq':
                selected_choice_id = request.POST.get(f'question_{question.id}')
                selected_choice = None
                marks_awarded = 0.0
                if selected_choice_id:
                    selected_choice = QuizChoice.objects.filter(id=selected_choice_id, question=question).first()
                    if selected_choice and selected_choice.is_correct:
                        marks_awarded = float(question.marks)
                        total_score += marks_awarded

                QuizAnswer.objects.create(
                    submission=submission,
                    question=question,
                    selected_choice=selected_choice,
                    marks_awarded=marks_awarded
                )
            else:
                has_descriptive = True
                text_ans = request.POST.get(f'question_{question.id}_text', '').strip()
                QuizAnswer.objects.create(
                    submission=submission,
                    question=question,
                    text_response=text_ans,
                    marks_awarded=0.0
                )

        submission.obtained_marks = total_score
        # If all questions are MCQ, we can automatically mark it as graded!
        if not has_descriptive:
            submission.is_graded = True
            submission.teacher_feedback = "Auto-graded (All MCQ questions)."
        else:
            submission.is_graded = False
        submission.save()

        messages.success(request, "Quiz submitted successfully!")
        return render(request, 'evaluations/quiz_result.html', {'quiz': quiz, 'submission': submission})

    return render(request, 'evaluations/take_quiz.html', {'quiz': quiz, 'questions': questions})


@login_required
def submit_viva(request, viva_id):
    viva = get_object_or_404(VivaAssessment, id=viva_id, is_published=True)

    if not viva.course.students.filter(id=request.user.id).exists():
        messages.error(request, "You are not enrolled in this course.")
        return redirect('student_dashboard')

    existing_sub = VivaSubmission.objects.filter(viva=viva, student=request.user).first()

    if request.method == 'POST':
        if existing_sub and existing_sub.is_graded:
            messages.error(request, "This submission has already been graded and cannot be updated.")
            return redirect('student_course_detail', course_id=viva.course.id)

        form = VivaSubmissionForm(request.POST, request.FILES, instance=existing_sub)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.viva = viva
            sub.student = request.user
            sub.is_graded = False  # Needs re-grading if updated
            sub.save()
            messages.success(request, "Viva video submitted successfully! Your teacher will evaluate it.")
            return redirect('student_course_detail', course_id=viva.course.id)
    else:
        form = VivaSubmissionForm(instance=existing_sub)

    return render(request, 'evaluations/submit_viva.html', {
        'viva': viva,
        'form': form,
        'existing_sub': existing_sub,
    })


@login_required
def student_grade_report(request):
    if request.user.is_teacher:
        return redirect('teacher_dashboard')

    courses = request.user.enrolled_courses.all()
    reports = []

    for course in courses:
        mid_quizzes = Quiz.objects.filter(course=course, term=TermChoices.MIDTERM)
        mid_vivas = VivaAssessment.objects.filter(course=course, term=TermChoices.MIDTERM)
        fin_quizzes = Quiz.objects.filter(course=course, term=TermChoices.FINAL)
        fin_vivas = VivaAssessment.objects.filter(course=course, term=TermChoices.FINAL)

        # Midterm Marks
        mid_q_sub = QuizSubmission.objects.filter(quiz__in=mid_quizzes, student=request.user)
        mid_q_obtained = sum([float(s.obtained_marks) for s in mid_q_sub])
        mid_q_total = sum([q.total_marks for q in mid_quizzes])

        mid_v_sub = VivaSubmission.objects.filter(viva__in=mid_vivas, student=request.user, is_graded=True)
        mid_v_obtained = sum([float(s.obtained_marks or 0) for s in mid_v_sub])
        mid_v_total = sum([v.total_marks for v in mid_vivas])

        # Final Marks
        fin_q_sub = QuizSubmission.objects.filter(quiz__in=fin_quizzes, student=request.user)
        fin_q_obtained = sum([float(s.obtained_marks) for s in fin_q_sub])
        fin_q_total = sum([q.total_marks for q in fin_quizzes])

        fin_v_sub = VivaSubmission.objects.filter(viva__in=fin_vivas, student=request.user, is_graded=True)
        fin_v_obtained = sum([float(s.obtained_marks or 0) for s in fin_v_sub])
        fin_v_total = sum([v.total_marks for v in fin_vivas])

        total_obtained = mid_q_obtained + mid_v_obtained + fin_q_obtained + fin_v_obtained
        grand_total = mid_q_total + mid_v_total + fin_q_total + fin_v_total
        percentage = round((total_obtained / grand_total * 100), 1) if grand_total > 0 else 0

        reports.append({
            'course': course,
            'mid_q_obtained': mid_q_obtained,
            'mid_q_total': mid_q_total,
            'mid_v_obtained': mid_v_obtained,
            'mid_v_total': mid_v_total,
            'mid_total': mid_q_obtained + mid_v_obtained,
            'fin_q_obtained': fin_q_obtained,
            'fin_q_total': fin_q_total,
            'fin_v_obtained': fin_v_obtained,
            'fin_v_total': fin_v_total,
            'fin_total': fin_q_obtained + fin_v_obtained,
            'total_obtained': total_obtained,
            'grand_total': grand_total,
            'percentage': percentage,
        })

    return render(request, 'evaluations/student_grade_report.html', {'reports': reports})
