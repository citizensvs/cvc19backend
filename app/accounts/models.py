import math
import random

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from app.common.helpers import phone_number_valid


class EndUser(models.Model):
    phone = models.CharField(
        verbose_name="Phone Number", max_length=12, default=None, null=True, blank=True
    )
    user = models.ForeignKey(
        User, related_name="end_user", on_delete=models.CASCADE, null=True
    )


class OneTimePassword(models.Model):
    phone = models.CharField(verbose_name="OTP Phone Number", max_length=12)
    code = models.CharField(max_length=6)
    generated_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    @classmethod
    def generate_otp(cls, phone):
        phone_number_valid(phone)
        digits = "0123456789"
        otp = ""
        for i in range(6):
            otp += digits[math.floor(random.random() * 10)]
        cls.objects.create(phone=phone, code=otp)
        return otp

    @classmethod
    def validate_otp(cls, phone, otp):
        result = cls.objects.filter(phone=phone).last()
        if result and result.code == otp:
            result.used = True
            result.save()
            return True
        return False
