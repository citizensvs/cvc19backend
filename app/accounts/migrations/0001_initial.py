# Generated by Django 3.0.5 on 2020-04-08 18:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="OneTimePassword",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "phone",
                    models.CharField(max_length=12, verbose_name="OTP Phone Number"),
                ),
                ("code", models.CharField(max_length=6)),
                ("generated_at", models.DateTimeField(auto_now_add=True)),
                ("used", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="EndUser",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        default=None,
                        max_length=12,
                        null=True,
                        verbose_name="Phone Number",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="end_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
