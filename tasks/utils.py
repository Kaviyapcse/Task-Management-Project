import enum

from rest_framework import permissions
from tasks.models import Task, User


class HandlingMessages(enum.Enum):

    not_found = "{key} not found."
    success_msg = "{key} added successfully"
    update_msg = "{key} updated successfully"
    already_exists = "{key} already exists"
    delete_success = "{key} deleted successfully!"
    required = "{key} field is required"
    email_wrong = "Email is Wrong please check"
    password_wrong = "Password is Wrong please check"


class OnlyAdminPermission(permissions.BasePermission):

    message = 'Not authorized to perform this action'

    def has_permission(self, request, view):
        if request.user.role_type == User.ROLE_CHOICE[1][0]:
            if request.method == "GET":
                return True
            elif request.method == "PUT":
                return True
        else:
            return True
        return False
