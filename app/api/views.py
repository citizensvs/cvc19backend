from django.contrib.auth import logout
from django.contrib.auth.models import Group, User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from app.accounts.models import EndUser, OneTimePassword
from app.accounts.tokens import account_activation_token
from app.accounts.utils import create_user_account, get_and_authenticate_user
from app.api.permissions import IsOwner
from app.api.serializers import (
    AuthUserSerializer,
    EmptySerializer,
    EndUserSerializer,
    GroupSerializer,
    IssueSerializer,
    IssueTypeSerializer,
    PasswordChangeSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    UserSerializer,
)
from app.api.textlocal import send_sms
from app.common.helpers import normalize_phone_number
from app.issues.models import Issue, IssueSubType, IssueType


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
    permission_classes = [permissions.IsAdminUser]


class EndUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows end-users to be viewed or edited.
    """

    queryset = EndUser.objects.all()
    serializer_class = EndUserSerializer
    permission_classes = [permissions.IsAdminUser]


class IssueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows issues to be viewed or edited
    """

    serializer_class = IssueSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Issue.objects.filter(owner=self.request.user)


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


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = EmptySerializer
    serializer_classes = {
        "login": UserLoginSerializer,
        "register": UserRegisterSerializer,
        "password_change": PasswordChangeSerializer,
    }

    @action(methods=["POST"], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_and_authenticate_user(**serializer.validated_data)
        data = AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()

    @action(methods=["POST"], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user_account(**serializer.validated_data)
        data = AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(methods=["POST"], detail=False)
    def logout(self, request):
        if request.user.is_anonymous:
            return Response(
                data={"detail": "Missing token"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            request.user.auth_token.delete()
        except AttributeError:
            pass
        logout(request)
        data = {"success": "Logged out"}
        return Response(data=data, status=status.HTTP_200_OK)

    @action(
        methods=["PATCH"],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    def password_change(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data.get("new_password"))
        request.user.save()
        data = {"success": "Password changed"}
        return Response(data=data, status=status.HTTP_200_OK)


class OTP(View):
    # authentication_classes = [permissions.AllowAny]

    @staticmethod
    def get(request):
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

    @staticmethod
    def post(request):
        phone = request.POST.get("phone")
        otp = request.POST.get("otp")
        if phone and otp:
            phone = normalize_phone_number(phone)
            if OneTimePassword.validate_otp(phone, otp):
                EndUser.objects.get_or_create(phone=phone)
                return JsonResponse({"success": True})
            return JsonResponse({"error": "incorrect OTP", "success": False})
        return JsonResponse({"error": "invalid input", "success": False})


class Email(APIView):
    @staticmethod
    def get(request):
        user = request.user
        current_site = get_current_site(request)
        subject = "Activate Your MySite Account"
        message = render_to_string(
            "emails/account_activation_email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        user.email_user(subject, message)
        # send_mail(
        #     "Subject here",
        #     "Here is the message.",
        #     "hello@penciljar.studio",
        #     ["arjunmunji@gmail.com"],
        #     fail_silently=False,
        # )
