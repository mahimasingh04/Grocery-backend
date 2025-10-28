from rest_framework import permissions

class IsStoreManager(permissions.BasePermission):
    """
    Custom permission: only users with role='manager' can create, update, or delete products.
    Authenticated users can only view (GET).
    """

    def has_permission(self, request, view):
       
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        
        return (
            request.user 
            and request.user.is_authenticated 
            and getattr(request.user, 'role', None) == 'manager'
        )


