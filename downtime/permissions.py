from rest_framework.permissions import IsAdminUser, SAFE_METHODS

# from https://stackoverflow.com/questions/37968770/django-rest-framework-permission-isadminorreadonly
class IsAdminUserOrReadOnly(IsAdminUser):

    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        return request.method in SAFE_METHODS or is_admin