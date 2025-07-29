from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Student

def student_list(request):
    students = Student.objects.all()
    return render(request, 'student_list.html', {'students': students})

def add_student(request):
    if request.method == 'POST':
        name = request.POST['name']
        roll = request.POST['roll']
        email = request.POST['email']
        course = request.POST['course']
        Student.objects.create(name=name, roll=roll, email=email, course=course)
        return redirect('/')
    return render(request, 'add_student.html')

def update_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.name = request.POST['name']
        student.roll = request.POST['roll']
        student.email = request.POST['email']
        student.course = request.POST['course']
        student.save()
        return redirect('/')
    return render(request, 'update_student.html', {'student': student})

def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('/')
