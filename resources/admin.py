from django.contrib import admin
from .models import Skill, Resource, ResourceSkill

class ResourceSkillInline(admin.TabularInline):
    model = ResourceSkill
    extra = 1

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'capacity')
    search_fields = ('name', 'role')
    inlines = [ResourceSkillInline]

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)