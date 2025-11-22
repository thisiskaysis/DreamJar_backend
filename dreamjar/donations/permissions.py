from rest_framework import permissions

class IsDonorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow donors of a donation to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.donor == request.user