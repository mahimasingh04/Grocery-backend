from rest_framework import permissions

class IsStoreManager(permissions.BasePermission):
    """
    Custom permission: only users with role='manager' can create, update, or delete products.
    Authenticated users can only view (GET).
    """

    def has_permission(self, request, view):
        # Allow all authenticated users to view (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # For write actions — user must be authenticated AND role == 'manager'
        return (
            request.user 
            and request.user.is_authenticated 
            and getattr(request.user, 'role', None) == 'manager'
        )


