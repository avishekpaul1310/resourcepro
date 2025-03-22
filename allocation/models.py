from django.db import models
from resources.models import Resource
from projects.models import Task

class Assignment(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='assignments')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    allocated_hours = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.resource.name} assigned to {self.task.name}"
    
    class Meta:
        unique_together = ['resource', 'task']