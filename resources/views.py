from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Resource, Skill, ResourceSkill
from .forms import ResourceForm, ResourceSkillFormSet

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
    
    return render(request, 'resources/resource_detail.html', {'resource': resource})

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