from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, date
from .models import Resource, Skill, ResourceSkill, TimeEntry, ResourceAvailability
from .forms import ResourceForm, ResourceSkillFormSet, TimeEntryForm, ResourceAvailabilityForm, BulkTimeEntryForm

@login_required
def resource_list(request):
    """List all resources"""
    resources = Resource.objects.all()
    for resource in resources:
        resource.utilization = resource.current_utilization()
    
    return render(request, 'resources/resource_list.html', {'resources': resources})

@login_required
def resource_detail(request, pk):
    """Detail view for a resource"""
    resource = get_object_or_404(Resource, pk=pk)
    resource.utilization = resource.current_utilization()
    
    # Get recent time entries
    recent_time_entries = resource.time_entries.order_by('-date')[:10]
    
    # Get upcoming availability
    upcoming_availability = resource.availability.filter(
        start_date__gte=timezone.now().date()
    ).order_by('start_date')[:5]
    
    context = {
        'resource': resource,
        'recent_time_entries': recent_time_entries,
        'upcoming_availability': upcoming_availability
    }
    
    return render(request, 'resources/resource_detail.html', context)

@login_required
def resource_create(request):
    """Create a new resource"""
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        formset = ResourceSkillFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            resource = form.save()
            formset.instance = resource
            formset.save()
            messages.success(request, 'Resource created successfully.')
            return redirect('resource_detail', pk=resource.pk)
    else:
        form = ResourceForm()
        formset = ResourceSkillFormSet()
    
    return render(request, 'resources/resource_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create Resource'
    })

@login_required
def resource_edit(request, pk):
    """Edit an existing resource"""
    resource = get_object_or_404(Resource, pk=pk)
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource)
        formset = ResourceSkillFormSet(request.POST, instance=resource)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Resource updated successfully.')
            return redirect('resource_detail', pk=resource.pk)
    else:
        form = ResourceForm(instance=resource)
        formset = ResourceSkillFormSet(instance=resource)
    
    return render(request, 'resources/resource_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Edit Resource'
    })

@login_required
def create_skill(request):
    """Create a new skill via AJAX"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        skill_name = request.POST.get('skill_name')
        description = request.POST.get('description', '')
        
        if not skill_name:
            return JsonResponse({'success': False, 'error': 'Skill name is required'}, status=400)
            
        # Check if skill with this name already exists
        if Skill.objects.filter(name=skill_name).exists():
            return JsonResponse({'success': False, 'error': 'Skill with this name already exists'}, status=400)
            
        # Create new skill
        skill = Skill.objects.create(name=skill_name, description=description)
        
        # Return success with skill data
        return JsonResponse({
            'success': True,
            'skill': {
                'id': skill.id,
                'name': skill.name,
                'description': skill.description
            }
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def skill_list(request):
    """List all skills with option to delete them"""
    skills = Skill.objects.all()
    
    # Count resources using each skill for reference
    for skill in skills:
        skill.usage_count = ResourceSkill.objects.filter(skill=skill).count()
    
    return render(request, 'resources/skill_list.html', {'skills': skills})

@login_required
def skill_delete(request, pk):
    """Delete a skill"""
    skill = get_object_or_404(Skill, pk=pk)
    
    # Check if any resources are using this skill
    usage_count = ResourceSkill.objects.filter(skill=skill).count()
    
    if request.method == 'POST':
        skill_name = skill.name
        skill.delete()
        messages.success(request, f'Skill "{skill_name}" deleted successfully.')
        return redirect('skill_list')
    
    return render(request, 'resources/skill_confirm_delete.html', {
        'skill': skill,
        'usage_count': usage_count
    })

@login_required
def time_entry_list(request):
    """List time entries with filtering"""
    time_entries = TimeEntry.objects.select_related('resource', 'task').order_by('-date')
    
    # Filter by resource if provided
    resource_id = request.GET.get('resource')
    if resource_id:
        time_entries = time_entries.filter(resource_id=resource_id)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        time_entries = time_entries.filter(date__gte=start_date)
    if end_date:
        time_entries = time_entries.filter(date__lte=end_date)
    
    # Pagination
    time_entries = time_entries[:50]  # Limit to 50 entries
    
    resources = Resource.objects.all()
    
    context = {
        'time_entries': time_entries,
        'resources': resources,
        'selected_resource': resource_id,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'resources/time_entry_list.html', context)

@login_required
def time_entry_create(request):
    """Create a new time entry"""
    if request.method == 'POST':
        form = TimeEntryForm(request.POST, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Time entry recorded successfully.')
            return redirect('time_entry_list')
    else:
        form = TimeEntryForm(user=request.user)
    
    return render(request, 'resources/time_entry_form.html', {
        'form': form,
        'title': 'Record Time Entry'
    })

@login_required
def time_entry_edit(request, pk):
    """Edit an existing time entry"""
    time_entry = get_object_or_404(TimeEntry, pk=pk)
    
    if request.method == 'POST':
        form = TimeEntryForm(request.POST, instance=time_entry, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Time entry updated successfully.')
            return redirect('time_entry_list')
    else:
        form = TimeEntryForm(instance=time_entry, user=request.user)
    
    return render(request, 'resources/time_entry_form.html', {
        'form': form,
        'title': 'Edit Time Entry'
    })

@login_required
def bulk_time_entry(request):
    """Create multiple time entries for a date range"""
    if request.method == 'POST':
        form = BulkTimeEntryForm(request.POST, user=request.user)
        
        if form.is_valid():
            # Create time entries for each day in the range
            resource = form.cleaned_data['resource']
            task = form.cleaned_data['task']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            hours_per_day = form.cleaned_data['hours_per_day']
            description = form.cleaned_data['description']
            
            created_count = 0
            current_date = start_date
            
            while current_date <= end_date:
                # Skip weekends if desired (optional)
                if current_date.weekday() < 5:  # Monday to Friday
                    time_entry, created = TimeEntry.objects.get_or_create(
                        resource=resource,
                        task=task,
                        date=current_date,
                        defaults={
                            'hours': hours_per_day,
                            'description': description
                        }
                    )
                    if created:
                        created_count += 1
                
                current_date += timedelta(days=1)
            
            messages.success(request, f'Created {created_count} time entries.')
            return redirect('time_entry_list')
    else:
        form = BulkTimeEntryForm(user=request.user)
    
    return render(request, 'resources/bulk_time_entry_form.html', {
        'form': form,
        'title': 'Bulk Time Entry'
    })

@login_required
def availability_calendar(request):
    """Display availability calendar"""
    resource_id = request.GET.get('resource')
    
    # Get availability data for next 30 days
    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=30)
    
    availability_data = ResourceAvailability.objects.filter(
        start_date__lte=end_date,
        end_date__gte=start_date
    ).select_related('resource')
    
    if resource_id:
        availability_data = availability_data.filter(resource_id=resource_id)
    
    resources = Resource.objects.all()
    
    context = {
        'availability_data': availability_data,
        'resources': resources,
        'selected_resource': resource_id,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'resources/availability_calendar.html', context)

@login_required
def availability_create(request):
    """Create availability entry"""
    if request.method == 'POST':
        form = ResourceAvailabilityForm(request.POST, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Availability updated successfully.')
            return redirect('availability_calendar')
    else:
        form = ResourceAvailabilityForm(user=request.user)
    
    return render(request, 'resources/availability_form.html', {
        'form': form,
        'title': 'Add Availability'
    })

@login_required
def availability_edit(request, pk):
    """Edit availability entry"""
    availability = get_object_or_404(ResourceAvailability, pk=pk)
    
    if request.method == 'POST':
        form = ResourceAvailabilityForm(request.POST, instance=availability)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Availability updated successfully.')
            return redirect('availability_calendar')
    else:
        form = ResourceAvailabilityForm(instance=availability)
    
    return render(request, 'resources/availability_form.html', {
        'form': form,
        'title': 'Edit Availability'
    })

@login_required
def resource_time_tracking_report(request, pk):
    """Generate time tracking report for a specific resource"""
    resource = get_object_or_404(Resource, pk=pk)
    
    # Get date range from query parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Default to current month if no dates provided
    if not start_date or not end_date:
        today = timezone.now().date()
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    else:
        try:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format. Using current month.')
            today = timezone.now().date()
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    # Get time entries for the resource in the date range
    time_entries = resource.time_entries.filter(
        date__gte=start_date,
        date__lte=end_date
    ).select_related('task', 'task__project').order_by('-date')
    
    # Calculate summary statistics
    total_hours = sum(entry.hours for entry in time_entries)
    total_days = len(set(entry.date for entry in time_entries))
    
    # Group by project
    project_hours = {}
    for entry in time_entries:
        project_name = entry.task.project.name
        if project_name not in project_hours:
            project_hours[project_name] = 0
        project_hours[project_name] += float(entry.hours)
    
    context = {
        'resource': resource,
        'time_entries': time_entries,
        'start_date': start_date,
        'end_date': end_date,
        'total_hours': total_hours,
        'total_days': total_days,
        'project_hours': project_hours,
        'average_hours_per_day': round(total_hours / total_days, 2) if total_days > 0 else 0,
    }
    
    return render(request, 'resources/time_tracking_report.html', context)
