from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Semester
from .forms import CourseForm

@login_required
def create_course(request):
    if not (request.user.is_teacher or request.user.is_staff):
        messages.error(request, "Only teachers can create courses.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            form.save_m2m()  # Save students relation
            messages.success(request, f"Course '{course.code}: {course.title}' created successfully!")
            return redirect('teacher_course_detail', course_id=course.id)
    else:
        form = CourseForm()

    return render(request, 'academics/course_form.html', {'form': form})

@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.code}' updated successfully!")
            return redirect('teacher_course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)

    return render(request, 'academics/course_form.html', {'form': form, 'course': course})
