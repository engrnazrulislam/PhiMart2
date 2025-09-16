# from rest_framework.permissions import BasePermission # এর পরিবর্তে 
from rest_framework import permissions

# class IsAdminOrReadOnly(BasePermission):
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # if request.method == 'GET': # এর পরিবর্তে
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool (request.user and request.user.is_staff)

class FullDjangoModelPermission(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map['GET'] = ['%(app_label)s.add_%(model_name)s']
        