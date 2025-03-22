from django import forms
from .models import Assignment
from resources.models import Resource
from projects.models import Task

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['resource', 'task', 'allocated_hours', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active tasks
        self.fields['task'].queryset = Task.objects.filter(
            status__in=['not_started', 'in_progress', 'blocked']
        )
        
        # Add estimated hours as help text for task field
        self.fields['task'].label_from_instance = lambda obj: f"{obj.name} ({obj.project.name}, {obj.estimated_hours}h)"