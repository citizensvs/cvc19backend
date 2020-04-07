from django.db import models
from django.forms import ChoiceField
from django.contrib.auth.models import User


STATUS_CHOICES = (
    ("active", "Active"),
    ("pending", "Pending"),
    ("resolved", "Resolved"),
    ("fraud", "Fraud"),
)

PRIORITY_LEVEL_CHOICES = (
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("critical", "Critical"),
)


class IssueType(models.Model):
    name = models.CharField(
        verbose_name="Issue Type Name",
        max_length=256,
        unique=True,
        blank=False,
        null=False,
    )


class IssueSubType(models.Model):
    name = models.CharField(
        verbose_name="Issue Sub Type Name",
        max_length=256,
        unique=True,
        blank=False,
        null=False,
    )
    parent = models.ForeignKey(
        IssueType, related_name="child_issue_type", on_delete=models.CASCADE
    )


class Issue(models.Model):
    title = models.CharField(verbose_name="Issue Title", max_length=256)
    description = models.TextField(verbose_name="Issue Description", max_length=1000)
    status = ChoiceField(choices=STATUS_CHOICES)
    priority = ChoiceField(choices=PRIORITY_LEVEL_CHOICES)
    type = models.ForeignKey(
        IssueType, related_name="issues", on_delete=models.SET_NULL, null=True
    )
    sub_type = models.ForeignKey(
        IssueSubType, related_name="+", on_delete=models.SET_NULL, null=True
    )
    created_by = models.ForeignKey(
        User, related_name="created_issues", on_delete=models.SET_NULL, null=True
    )
    reviewed_by = models.ForeignKey(
        User, related_name="reviewed_issues", on_delete=models.SET_NULL, null=True
    )
