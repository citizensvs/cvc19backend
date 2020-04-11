from django.contrib.auth.models import User
from django.db import models

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


class OwnedModel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class LocationModel(models.Model):
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)

    class Meta:
        abstract = True


class IssueType(models.Model):
    name = models.CharField(
        verbose_name="Issue Type Name",
        max_length=200,
        unique=True,
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.name


class IssueSubType(models.Model):
    name = models.CharField(
        verbose_name="Issue Sub Type Name",
        max_length=200,
        unique=True,
        blank=False,
        null=False,
    )
    parent = models.ForeignKey(
        IssueType, related_name="child_issue_type", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Issue(OwnedModel, LocationModel):
    title = models.CharField(verbose_name="Issue Title", max_length=256)
    description = models.TextField(verbose_name="Issue Description", max_length=1000)
    status = models.CharField(choices=STATUS_CHOICES, default="", max_length=100)
    priority = models.CharField(
        choices=PRIORITY_LEVEL_CHOICES, default="medium", max_length=100
    )
    type = models.ForeignKey(
        IssueType, related_name="issues", on_delete=models.SET_NULL, null=True
    )
    sub_type = models.ForeignKey(
        IssueSubType, related_name="+", on_delete=models.SET_NULL, null=True
    )
    reviewed_by = models.ForeignKey(
        User, related_name="reviewed_issues", on_delete=models.SET_NULL, null=True
    )
