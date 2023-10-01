from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedOrPublic(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.id == obj.author.id:
            return True
        if request.method in SAFE_METHODS and obj.public:
            return True
        return False


class UserPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.method == "POST" and not request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.id == obj.id:
            return True
        if request.method in SAFE_METHODS:
            return True
        return False
