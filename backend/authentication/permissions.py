from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission class to allow only admin users
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsStaffUser(permissions.BasePermission):
    """
    Permission class to allow only staff users
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to the owner
        # Assumes the object has a 'user' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class CanAccessPatientData(permissions.BasePermission):
    """
    Permission to control access to patient data
    Only staff members can access patient data
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        # Staff members can access all patient data
        return request.user and request.user.is_authenticated and request.user.is_staff


class CanManageTreatments(permissions.BasePermission):
    """
    Permission to manage treatments
    Only staff members can manage treatments
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return request.user and request.user.is_authenticated and request.user.is_staff


class CanManageFinances(permissions.BasePermission):
    """
    Permission to manage financial records
    Only admin and authorized staff can manage finances
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated and request.user.is_staff
        
        return request.user and request.user.is_authenticated and request.user.is_staff
