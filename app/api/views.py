from django.contrib.auth.models import User, Group
from django.views import View
from app.accounts.models import EndUser
from app.issues.models import IssueType, IssueSubType
from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin
from rest_framework import permissions
from app.api.serializers import (
    UserSerializer,
    GroupSerializer,
    EndUserSerializer,
    IssueTypeSerializer,
    IssueSubTypeSerializer,
)
from django.http.response import JsonResponse
from app.accounts.models import OneTimePassword
from app.api.twilio import send_sms


class UserViewSet(viewsets.ModelViewSet, CreateModelMixin):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = []
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class EndUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows end-users to be viewed or edited.
    """

    queryset = EndUser.objects.all()
    serializer_class = EndUserSerializer
    permission_classes = [permissions.IsAuthenticated]


class IssueTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows issue types to be viewed or edited.
    """

    queryset = IssueType.objects.all()
    serializer_class = IssueTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class IssueSubTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows issue sub-types to be viewed or edited.
    """

    queryset = IssueSubType.objects.all()
    serializer_class = IssueTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class OTP(View):
    def get(self, request):
        phone = request.GET.get("phone")
        if phone:
            otp = OneTimePassword.generate_otp(phone)
            send_sms(phone, otp)
            return JsonResponse({'success': True})

    def post(self, request):
        phone = request.POST.get("phone")
        otp = request.POST.get("otp")
        if phone and otp:
            if OneTimePassword.validate_otp(phone, otp):
                return JsonResponse({"valid": True})
            return JsonResponse({'error': 'incorrect OTP'})
        return JsonResponse({'error': 'invalid input'})
