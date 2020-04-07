from django.contrib.auth.models import User, Group
from rest_framework import routers, serializers, viewsets
from app.issues.models import IssueType, IssueSubType
from app.accounts.models import EndUser


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


class IssueTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IssueType
        fields = ["url", "name"]


class IssueSubTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IssueSubType
        fields = ["url", "name", "parent"]
