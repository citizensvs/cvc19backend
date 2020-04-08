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
from app.api.textlocal import send_sms
from app.common.helpers import normalize_phone_number


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
            phone = normalize_phone_number(phone)
            existing_user = EndUser.objects.filter(phone=phone).first()
            if existing_user:
                if existing_user.user:
                    return JsonResponse(
                        {"username": existing_user.user.username, "success": True}
                    )
                return JsonResponse({"success": False, "error": "OTP verified"})
            otp_text = "OTP for CVC19 is {}"
            existing_otp = OneTimePassword.objects.filter(
                phone=phone, used=False
            ).first()
            if existing_otp:
                otp_text = otp_text.format(existing_otp)
            else:
                otp_text = otp_text.format(OneTimePassword.generate_otp(phone))
            send_sms(phone, otp_text)
            return JsonResponse({"success": True})
        return JsonResponse({"error": "invalid input", "success": False})

    def post(self, request):
        phone = request.POST.get("phone")
        otp = request.POST.get("otp")
        if phone and otp:
            phone = normalize_phone_number(phone)
            if OneTimePassword.validate_otp(phone, otp):
                EndUser.objects.get_or_create(phone=phone)
                return JsonResponse({"success": True})
            return JsonResponse({"error": "incorrect OTP", "success": False})
        return JsonResponse({"error": "invalid input", "success": False})
