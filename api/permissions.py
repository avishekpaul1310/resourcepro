"""
Custom permissions for ResourcePro API
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsResourceOwnerOrManager(permissions.BasePermission):
    """
    Permission for resource-specific operations.
    Users can only access their own resource data unless they're managers.
    """
    
    def has_object_permission(self, request, view, obj):
        # Managers (staff users) have full access
        if request.user.is_staff:
            return True
        
        # Users can access their own resource
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # For read-only access, allow if user is authenticated
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False


class IsProjectManagerOrReadOnly(permissions.BasePermission):
    """
    Permission for project-specific operations.
    Only project managers can edit projects.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for project manager or staff
        if request.user.is_staff:
            return True
        
        if hasattr(obj, 'manager') and obj.manager == request.user:
            return True
        
        return False


class CanManageAssignments(permissions.BasePermission):
    """
    Permission for assignment operations.
    Users can manage assignments for their own resources or projects they manage.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Staff users have full access
        if request.user.is_staff:
            return True
        
        # Resource owners can manage their assignments
        if hasattr(obj, 'resource') and hasattr(obj.resource, 'user') and obj.resource.user == request.user:
            return True
        
        # Project managers can manage assignments for their projects
        if hasattr(obj, 'task') and hasattr(obj.task, 'project') and obj.task.project.manager == request.user:
            return True
        
        # Read-only access for others
        return request.method in permissions.SAFE_METHODS


class CanViewTimeEntries(permissions.BasePermission):
    """
    Permission for time entry operations.
    Users can only view/edit their own time entries unless they're managers.
    """
    
    def has_object_permission(self, request, view, obj):
        # Staff users have full access
        if request.user.is_staff:
            return True
        
        # Resource owners can manage their time entries
        if hasattr(obj, 'resource') and hasattr(obj.resource, 'user') and obj.resource.user == request.user:
            return True
        
        # Project managers can view time entries for their projects
        if (request.method in permissions.SAFE_METHODS and 
            hasattr(obj, 'task') and hasattr(obj.task, 'project') and 
            obj.task.project.manager == request.user):
            return True
        
        return False


class APIKeyPermission(permissions.BasePermission):
    """
    Permission class for API key authentication.
    """
    
    def has_permission(self, request, view):
        # Check for API key in headers
        api_key = request.META.get('HTTP_X_API_KEY')
        if api_key:
            # Validate API key here (implement your own logic)
            # For now, we'll use token authentication
            return request.user.is_authenticated
        
        # Fall back to regular authentication
        return request.user.is_authenticated
