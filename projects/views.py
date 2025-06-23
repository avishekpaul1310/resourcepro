from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Task
from .forms import ProjectForm, TaskForm

@login_required
def project_list(request):
    """List all projects"""
    projects = Project.objects.all()
    
    return render(request, 'projects/project_list.html', {'projects': projects})

@login_required
def project_detail(request, pk):
    """Detail view for a project"""
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all()
    
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'tasks': tasks
    })

@login_required
def project_create(request):
    """Create a new project"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, 'Project created successfully.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'projects/project_form.html', {
        'form': form,
        'title': 'Create Project'
    })

@login_required
def project_edit(request, pk):
    """Edit an existing project"""
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/project_form.html', {
        'form': form,
        'title': 'Edit Project'
    })

@login_required
def project_delete(request, pk):
    """Delete a project"""
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project "{project_name}" deleted successfully.')
        return redirect('project_list')
    
    return render(request, 'projects/project_confirm_delete.html', {
        'project': project
    })

@login_required
def task_list(request):
    """List all tasks"""
    tasks = Task.objects.all()
    
    return render(request, 'projects/task_list.html', {'tasks': tasks})

@login_required
def task_detail(request, pk):
    """Detail view for a task"""
    task = get_object_or_404(Task, pk=pk)
    
    return render(request, 'projects/task_detail.html', {'task': task})

@login_required
def task_create(request):
    """Create a new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, 'Task created successfully.')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm()
    
    return render(request, 'projects/task_form.html', {
        'form': form,
        'title': 'Create Task'
    })

@login_required
def task_edit(request, pk):
    """Edit an existing task"""
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'projects/task_form.html', {
        'form': form,
        'title': 'Edit Task'
    })