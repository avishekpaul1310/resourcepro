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
            'status', 'priority',
            'completion_percentage'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'skills_required': forms.SelectMultiple(attrs={'class': 'select2'}),
            'completion_percentage': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }