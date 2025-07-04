from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.utils import timezone
from django.http import JsonResponse
import datetime
from django_filters.rest_framework import DjangoFilterBackend
from loan_app_backend.apps.loanapp.emails import send_email
from loan_app_backend.apps.loanapp.models import Users, LoanApplication, FraudFlag
from loan_app_backend.apps.loanapp.serializers import LoanApplicationSerializer
from loan_app_backend.apps.common.filter import GenericFilterSet
from loan_app_backend.apps.common.pagination import GenericPagination
from django.conf import settings


class LoanApplicationFilter(GenericFilterSet):
    class Meta:
        model = LoanApplication
        fields = ['status', 'created_at']
        text_search_fields = ['status']
        date_fields = ['created_at']
        boolean_fields = []


class LoanApplicationView(generics.ListCreateAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = GenericPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = LoanApplicationFilter

    def get_queryset(self):
        return LoanApplication.objects.filter(user=self.request.user).order_by('-created_at')

    @extend_schema(
        summary="Submit Loan Request",
        request=LoanApplicationSerializer,
        responses={
            201: OpenApiResponse(description="Loan application created"),
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({
                "message": "Loan application failed.",
                "data": serializer.errors
            }, status=400)

        self.perform_create(serializer)
        return JsonResponse({
            "message": "Loan application submitted successfully.",
            "data": serializer.data
        }, status=201)

    def perform_create(self, serializer):
        user = self.request.user
        now = timezone.now()
        flagged = None
        reason = None

        # 1. More than 3 loans in last 24 hours
        if LoanApplication.objects.filter(user=user, created_at__gte=now - datetime.timedelta(hours=24)).count() >= 3:
            reason = "More than 3 loans in 24 hours"
            flagged = serializer.save(user=user, status='flagged')
            FraudFlag.objects.create(loan_application=flagged, reason=reason)

        # 2. Amount exceeds 5 million
        elif serializer.validated_data['amount_requested'] > 5_000_000:
            reason = "Amount exceeds NGN 5,000,000"
            flagged = serializer.save(user=user, status='flagged')
            FraudFlag.objects.create(loan_application=flagged, reason=reason)

        # 3. More than 10 users share the same email domain
        else:
            domain = user.email.split('@')[-1]
            users_with_same_domain = Users.objects.filter(email__iendswith=f'@{domain}').distinct()
            if users_with_same_domain.count() > 10:
                reason = "Email domain used by more than 10 users"
                flagged = serializer.save(user=user, status='flagged')
                FraudFlag.objects.create(loan_application=flagged, reason=reason)

        if flagged:
            send_email(
                subject="🚨 Flagged Loan Detected",
                message=(
                    f"Flagged Loan Alert\n\n"
                    f"User: {user.email}\n"
                    f"Amount: {serializer.validated_data['amount_requested']}\n"
                    f"Reason: {reason}"
                ),
                recipient_list=[settings.DEFAULT_FROM_EMAIL]
            )
        else:
            serializer.save(user=user, status='pending')
