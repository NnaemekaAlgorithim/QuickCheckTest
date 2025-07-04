from django.db import models
from django.contrib.auth.models import AbstractUser
from loan_app_backend.apps.common.models import BaseModel
from django.conf import settings
from django.utils import timezone


class Users(BaseModel, AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('user', 'User'),
    ], default='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} ({self.role})"


class LoanApplication(BaseModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("flagged", "Flagged")
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loan_applications"
    )
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.user.username} - {self.amount_requested}"


class FraudFlag(BaseModel):
    loan_application = models.ForeignKey(
        LoanApplication, on_delete=models.CASCADE, related_name="fraud_flags"
    )
    reason = models.CharField(max_length=255)

    def __str__(self):
        return f"Fraud: {self.reason}"


class ActivationCode(BaseModel):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=[('activation', 'Activation'), ('reset', 'Reset')])
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.purpose}"
