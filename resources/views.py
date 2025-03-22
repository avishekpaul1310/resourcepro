from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resource, Skill
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