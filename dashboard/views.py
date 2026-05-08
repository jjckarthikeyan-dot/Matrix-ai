from django.shortcuts import render, redirect
from .models import Task

def task_list(request):
    tasks = Task.objects.all().order_by('-created_at')
    return render(request, 'dashboard/task_list.html', {'tasks': tasks})

def task_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        if title and description:
            Task.objects.create(title=title, description=description)
            return redirect('task_list')
    return render(request, 'dashboard/task_form.html')
