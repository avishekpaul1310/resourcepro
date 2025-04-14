from django import forms
from .models import Project, Task

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'manager', 'status', 'priority', 'color']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'project', 'name', 'description', 
            'start_date', 'end_date', 
            'estimated_hours', 'skills_required',
            'status', 'priority', 'dependencies',
            'completion_percentage'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'skills_required': forms.SelectMultiple(attrs={'class': 'select2'}),
            'dependencies': forms.SelectMultiple(attrs={'class': 'select2'}),
            'completion_percentage': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Exclude self from dependencies list to prevent circular dependencies
            self.fields['dependencies'].queryset = Task.objects.exclude(pk=self.instance.pk)
        
        # Get the current project to filter dependencies if project is selected or instance has project
        project = None
        if self.data.get('project'):
            try:
                project_id = int(self.data.get('project'))
                project = Project.objects.get(id=project_id)
            except (ValueError, Project.DoesNotExist):
                pass
        elif self.instance and self.instance.project_id:
            project = self.instance.project
        
        if project:
            self.fields['dependencies'].queryset = Task.objects.filter(project=project)