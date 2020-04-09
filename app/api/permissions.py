from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    message = "Not an owner"

    def has_object_permission(self, request, view, obj):
        print("herere", obj.id)
        return request.user == obj.owner
