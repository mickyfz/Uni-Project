import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uni_portal.settings')
django.setup()

from django.core.files.base import ContentFile
from core.models import CustomUser
from academics.models import Semester, Course
from evaluations.models import (
    Quiz, QuizQuestion, QuizChoice, QuizSubmission, QuizAnswer,
    VivaAssessment, VivaSubmission, TermChoices, QuestionType
)

def run():
    print("Seeding University Portal sample data...")

    # 1. Superuser / Admin
    if not CustomUser.objects.filter(username='admin').exists():
        admin_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@uni.edu',
            password='admin123',
            first_name='System',
            last_name='Administrator',
            role=CustomUser.ROLE_TEACHER,
            university_id='ADM-001',
            department='Administration'
        )
        print("Created Superuser: admin / admin123")

    # 2. Teacher
    teacher, created = CustomUser.objects.get_or_create(
        username='teacher',
        defaults={
            'email': 'turing@uni.edu',
            'first_name': 'Alan',
            'last_name': 'Turing',
            'role': CustomUser.ROLE_TEACHER,
            'university_id': 'FAC-CSE-101',
            'department': 'Computer Science & Engineering',
            'phone': '+1-555-0199'
        }
    )
    if created:
        teacher.set_password('pass123')
        teacher.save()
        print("Created Teacher: teacher / pass123")

    # 3. Students
    student1, created = CustomUser.objects.get_or_create(
        username='student1',
        defaults={
            'email': 'alice@uni.edu',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'role': CustomUser.ROLE_STUDENT,
            'university_id': 'STU-2026-001',
            'department': 'Computer Science & Engineering',
            'phone': '+1-555-0101'
        }
    )
    if created:
        student1.set_password('pass123')
        student1.save()
        print("Created Student 1: student1 / pass123")

    student2, created = CustomUser.objects.get_or_create(
        username='student2',
        defaults={
            'email': 'bob@uni.edu',
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'role': CustomUser.ROLE_STUDENT,
            'university_id': 'STU-2026-002',
            'department': 'Computer Science & Engineering',
            'phone': '+1-555-0102'
        }
    )
    if created:
        student2.set_password('pass123')
        student2.save()
        print("Created Student 2: student2 / pass123")

    # 4. Semester
    semester, _ = Semester.objects.get_or_create(
        name='Spring 2026',
        defaults={'is_active': True}
    )

    # 5. Course
    course, created = Course.objects.get_or_create(
        code='CSE-301',
        defaults={
            'title': 'Data Structures & Algorithms',
            'description': 'Fundamental data structures (trees, graphs, heaps) and algorithm analysis techniques.',
            'semester': semester,
            'teacher': teacher
        }
    )
    course.students.add(student1, student2)
    course.save()
    print("Created Course: CSE-301 with 2 enrolled students")

    # 6. Midterm Quiz
    mid_quiz, created = Quiz.objects.get_or_create(
        course=course,
        term=TermChoices.MIDTERM,
        title='Midterm Quiz: Binary Trees & Stacks',
        defaults={
            'instructions': 'Answer all questions. Each MCQ has 1 correct answer. Total duration is 25 minutes.',
            'total_marks': 15,
            'duration_minutes': 25,
            'is_published': True
        }
    )
    if created:
        # Question 1 (MCQ)
        q1 = QuizQuestion.objects.create(
            quiz=mid_quiz,
            question_text='Which data structure follows the Last-In First-Out (LIFO) principle?',
            question_type=QuestionType.MCQ,
            marks=5,
            order=1
        )
        QuizChoice.objects.create(question=q1, choice_text='Queue', is_correct=False)
        QuizChoice.objects.create(question=q1, choice_text='Stack', is_correct=True)
        QuizChoice.objects.create(question=q1, choice_text='Linked List', is_correct=False)
        QuizChoice.objects.create(question=q1, choice_text='Binary Tree', is_correct=False)

        # Question 2 (MCQ)
        q2 = QuizQuestion.objects.create(
            quiz=mid_quiz,
            question_text='What is the worst-case time complexity of searching in a Binary Search Tree (BST)?',
            question_type=QuestionType.MCQ,
            marks=5,
            order=2
        )
        QuizChoice.objects.create(question=q2, choice_text='O(1)', is_correct=False)
        QuizChoice.objects.create(question=q2, choice_text='O(log n)', is_correct=False)
        QuizChoice.objects.create(question=q2, choice_text='O(n)', is_correct=True)
        QuizChoice.objects.create(question=q2, choice_text='O(n^2)', is_correct=False)

        # Question 3 (Descriptive)
        q3 = QuizQuestion.objects.create(
            quiz=mid_quiz,
            question_text='Briefly explain the difference between a Complete Binary Tree and a Full Binary Tree.',
            question_type=QuestionType.SHORT_ANSWER,
            marks=5,
            order=3
        )
        print("Created Midterm Quiz with 3 questions.")

    # 7. Midterm Viva Assessment
    mid_viva, created = VivaAssessment.objects.get_or_create(
        course=course,
        term=TermChoices.MIDTERM,
        title='Midterm Viva: Tree Traversals & Implementation',
        defaults={
            'description': (
                "Please record a 2 to 4 minute video answering the following questions on camera:\n"
                "1. Introduce yourself with your full name and student ID.\n"
                "2. Explain Inorder, Preorder, and Postorder traversals with a simple binary tree diagram.\n"
                "3. Explain why recursion is naturally suited for binary tree operations and how stack overflow can occur."
            ),
            'total_marks': 25,
            'is_published': True
        }
    )
    if created:
        print("Created Midterm Viva Assessment.")

    # 8. Final Quiz
    final_quiz, created = Quiz.objects.get_or_create(
        course=course,
        term=TermChoices.FINAL,
        title='Final Quiz: Graph Theory & Dynamic Programming',
        defaults={
            'instructions': 'Final examination quiz. Answer all questions within 30 minutes.',
            'total_marks': 20,
            'duration_minutes': 30,
            'is_published': True
        }
    )
    if created:
        q_f1 = QuizQuestion.objects.create(
            quiz=final_quiz,
            question_text="Which algorithm is used to find the shortest path in a weighted graph with non-negative edge weights?",
            question_type=QuestionType.MCQ,
            marks=10,
            order=1
        )
        QuizChoice.objects.create(question=q_f1, choice_text="Prim's Algorithm", is_correct=False)
        QuizChoice.objects.create(question=q_f1, choice_text="Kruskal's Algorithm", is_correct=False)
        QuizChoice.objects.create(question=q_f1, choice_text="Dijkstra's Algorithm", is_correct=True)
        QuizChoice.objects.create(question=q_f1, choice_text="Breadth First Search (BFS)", is_correct=False)

        q_f2 = QuizQuestion.objects.create(
            quiz=final_quiz,
            question_text="What are the two key properties required for a problem to be solved using Dynamic Programming?",
            question_type=QuestionType.SHORT_ANSWER,
            marks=10,
            order=2
        )
        print("Created Final Quiz.")

    # 9. Final Viva Assessment
    final_viva, created = VivaAssessment.objects.get_or_create(
        course=course,
        term=TermChoices.FINAL,
        title='Final Viva: Capstone Project & Algorithm Defense',
        defaults={
            'description': (
                "Record a 3 to 5 minute video defense covering:\n"
                "1. Summary of your term project architecture and data structures used.\n"
                "2. Live screen capture/presentation of your code execution.\n"
                "3. Analysis of space and time complexities of your core functions."
            ),
            'total_marks': 35,
            'is_published': True
        }
    )
    if created:
        print("Created Final Viva Assessment.")

    # 10. Sample Student Submission for demonstration
    # Let's seed a sample viva submission for student1 so the teacher can test grading immediately!
    existing_sub = VivaSubmission.objects.filter(viva=mid_viva, student=student1).first()
    if not existing_sub:
        sample_sub = VivaSubmission(
            viva=mid_viva,
            student=student1,
            notes="Timestamps:\n0:00 - Self introduction\n0:45 - Inorder traversal explanation\n1:50 - Recursion vs iterative stack discussion"
        )
        # Create a sample placeholder video file
        sample_video_content = b'Sample video placeholder bytes for student viva test.'
        sample_sub.video_file.save('alice_midterm_viva.mp4', ContentFile(sample_video_content), save=True)
        print("Created sample Viva Submission for student1 awaiting teacher evaluation.")

    print("\n--- SAMPLE DATA POPULATED SUCCESSFULLY ---")
    print("Logins available:")
    print("1. Teacher: username='teacher', password='pass123'")
    print("2. Student 1: username='student1', password='pass123'")
    print("3. Student 2: username='student2', password='pass123'")
    print("4. Admin: username='admin', password='admin123'")

if __name__ == '__main__':
    run()
