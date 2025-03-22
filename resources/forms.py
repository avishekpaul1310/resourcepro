from django import forms
from django.forms import inlineformset_factory
from .models import Resource, Skill, ResourceSkill

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['name', 'role', 'capacity', 'cost_per_hour', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
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