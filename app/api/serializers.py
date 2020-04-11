from django.contrib.auth import password_validation
from django.contrib.auth.models import BaseUserManager, Group, User
from rest_framework import routers, serializers, viewsets
from rest_framework.authtoken.models import Token

from app.accounts.models import EndUser
from app.issues.models import Issue, IssueSubType, IssueType


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    def create(self, validated_data):
        print("validated data", validated_data)

        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        return user

    class Meta:
        model = User
        fields = [
            "url",
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "groups",
        ]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class EndUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EndUser
        fields = ["url", "username", "email", "first_name", "last_name", "phone"]


class IssueTypeSerializer(serializers.ModelSerializer):
    class Meta:
        depth = 1
        model = IssueType
        fields = ["id", "name", "child_issue_type"]


class IssueSubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueSubType
        fields = ["id", "name"]


class IssueSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # type = serializers.StringRelatedField()
    # sub_type = serializers.StringRelatedField()

    def create(self, validated_data):
        print(validated_data)
        # validated_data['type'] = IssueType.objects.get(id=validated_data.pop("type"))
        # validated_data['sub_type'] = IssueSubType.objects.get(id=validated_data.pop("sub_type"))
        issue = Issue.objects.create(**validated_data)
        return issue

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "status",
            "type",
            "sub_type",
            "owner",
            "longitude",
            "latitude",
        ]


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(required=True, write_only=True)


class AuthUserSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "auth_token",
        )
        read_only_fields = ("id", "is_active", "is_staff")

    def get_auth_token(self, obj):
        token, _ = Token.objects.get_or_create(user=obj)
        return token.key


class EmptySerializer(serializers.Serializer):
    pass


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    A user serializer for registering the user
    """

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name")

    @staticmethod
    def validate_username(value):
        user = User.objects.filter(username=value)
        if user:
            raise serializers.ValidationError("Email is already taken")
        return value

    @staticmethod
    def validate_password(value):
        password_validation.validate_password(value)
        return value


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Current password does not match")
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value
