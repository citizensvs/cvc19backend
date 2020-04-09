from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from app.api import views

router = routers.DefaultRouter()
# router.register(r"users", views.UserViewSet)
# router.register(r"groups", views.GroupViewSet)
# router.register(r"end-users", views.EndUserViewSet)
router.register(r"issues", views.IssueViewSet, basename="")
router.register(r"issue-types", views.IssueTypeViewSet)
router.register(r"issue-sub-types", views.IssueSubTypeViewSet)
router.register(r"auth", views.AuthViewSet, basename="user-auth")

urlpatterns = [
    path("v1/", include(router.urls)),
    path("otp/", views.OTP.as_view()),
    path("email/", views.Email.as_view()),
]
