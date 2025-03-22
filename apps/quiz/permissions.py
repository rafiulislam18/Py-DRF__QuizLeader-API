from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    # Custom permission to allow only staff & superusers to write, edit & delete data
    def has_permission(self, request, view):
        # Allow all read-only requests (GET, HEAD, OPTIONS) for any user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write, edit & delete permissions are only allowed to staff & superusers
        return request.user and (request.user.is_staff or request.user.is_superuser)  # return True if the user is staff or superuser
