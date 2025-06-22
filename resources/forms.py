from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
import pytz
from .models import Resource, Skill, ResourceSkill, ResourceAvailability, TimeEntry
from projects.models import Task

# Common timezone choices for the dropdown
TIMEZONE_CHOICES = [
    ('UTC', 'UTC'),
    ('US/Eastern', 'US/Eastern (New York)'),
    ('US/Central', 'US/Central (Chicago)'),
    ('US/Mountain', 'US/Mountain (Denver)'),
    ('US/Pacific', 'US/Pacific (Los Angeles)'),
    ('Europe/London', 'Europe/London (UK)'),
    ('Europe/Paris', 'Europe/Paris (France)'),
    ('Europe/Berlin', 'Europe/Berlin (Germany)'),
    ('Asia/Tokyo', 'Asia/Tokyo (Japan)'),
    ('Asia/Shanghai', 'Asia/Shanghai (China)'),
    ('Asia/Kolkata', 'Asia/Kolkata (India)'),
    ('Australia/Sydney', 'Australia/Sydney'),
    ('America/Toronto', 'America/Toronto (Canada)'),
    ('America/Sao_Paulo', 'America/Sao_Paulo (Brazil)'),
]

class ResourceForm(forms.ModelForm):
    timezone = forms.ChoiceField(
        choices=TIMEZONE_CHOICES,
        initial='UTC',
        help_text="Select the timezone where this resource is located"
    )
    
    class Meta:
        model = Resource
        fields = ['name', 'role', 'capacity', 'cost_per_hour', 'color', 'timezone', 'location']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., New York, USA or Remote'}),
        }

class ResourceSkillForm(forms.ModelForm):
    class Meta:
        model = ResourceSkill
        fields = ['skill', 'proficiency']

# Create a formset for resource skills
ResourceSkillFormSet = inlineformset_factory(
    Resource,
    ResourceSkill,
    form=ResourceSkillForm,
    extra=1,
    can_delete=True
)

class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['resource', 'task', 'date', 'hours', 'description', 'is_billable']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'hours': forms.NumberInput(attrs={'step': '0.25', 'min': '0', 'max': '24'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'is_billable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter tasks to only show active ones
        self.fields['task'].queryset = Task.objects.filter(
            status__in=['not_started', 'in_progress']
        ).select_related('project')
        
        # If user is provided, filter resources
        if user and hasattr(user, 'resource'):
            self.fields['resource'].initial = user.resource
            self.fields['resource'].widget = forms.HiddenInput()
        
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()

class ResourceAvailabilityForm(forms.ModelForm):
    class Meta:
        model = ResourceAvailability
        fields = ['resource', 'start_date', 'end_date', 'availability_type', 'hours_per_day', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'hours_per_day': forms.NumberInput(attrs={'step': '0.5', 'min': '0', 'max': '24'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is provided and has a resource, set it as default
        if user and hasattr(user, 'resource'):
            self.fields['resource'].initial = user.resource
            self.fields['resource'].widget = forms.HiddenInput()
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")
        
        return cleaned_data

class BulkTimeEntryForm(forms.Form):
    """Form for entering time for multiple days at once"""
    resource = forms.ModelChoiceField(
        queryset=Resource.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    task = forms.ModelChoiceField(
        queryset=Task.objects.filter(status__in=['not_started', 'in_progress']),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    hours_per_day = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.25', 'min': '0', 'max': '24', 'class': 'form-control'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )
    is_billable = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    include_weekends = forms.BooleanField(
        required=False,
        initial=False,
        label="Include weekends",
        help_text="Check to include Saturday and Sunday in the date range",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user has a resource, set it as default and hide the field
        if user and hasattr(user, 'resource'):
            self.fields['resource'].initial = user.resource
            self.fields['resource'].widget = forms.HiddenInput()
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")
        
        # Check for maximum range (prevent abuse)
        if start_date and end_date:
            if (end_date - start_date).days > 30:
                raise forms.ValidationError("Date range cannot exceed 30 days.")
        
        return cleaned_data