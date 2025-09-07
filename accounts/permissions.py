from rest_framework.permissions import BasePermission
from .models import Roles

class IsProAuthor(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            request.user.role == Roles.PRO_AUTHOR
        )
