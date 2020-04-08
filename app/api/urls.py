from django.urls import path, include
from rest_framework import routers
from app.api import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)
router.register(r"end-users", views.EndUserViewSet)
router.register(r"issue-type", views.IssueTypeViewSet)
router.register(r"issue-sub-type", views.IssueSubTypeViewSet)

urlpatterns = [
    path("v1/", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
    path("otp/", views.OTP.as_view()),
]
