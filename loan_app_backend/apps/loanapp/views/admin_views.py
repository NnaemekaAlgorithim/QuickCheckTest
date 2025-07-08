from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from loan_app_backend.apps.loanapp.models import Users
from loan_app_backend.apps.loanapp.models import LoanApplication
from loan_app_backend.apps.loanapp.serializers import LoanApplicationSerializer, UserProfileSerializer
from loan_app_backend.apps.common.filter import GenericFilterSet
from loan_app_backend.apps.common.pagination import GenericPagination


class AdminUserListView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = GenericPagination
    queryset = Users.objects.all().order_by('-date_joined')
    filter_backends = [DjangoFilterBackend]
    filterset_class = type(
        'UserFilterSet',
        (GenericFilterSet,),
        {
            'Meta': type('Meta', (), {
                'model': Users,
                'fields': [],
            }),
            '__module__': __name__,
            '__doc__': 'Dynamic User filter'
        }
    )

    @extend_schema(summary="Admin View All Users", responses={200: UserProfileSerializer})
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminLoanListView(generics.ListAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = GenericPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = type(
        'LoanFilterSet',
        (GenericFilterSet,),
        {
            'Meta': type('Meta', (), {
                'model': LoanApplication,
                'fields': [],
            }),
            'text_search_fields': ['status'],
            'date_fields': ['created_at'],
            '__module__': __name__,
            '__doc__': 'Dynamic Loan filter'
        }
    )

    queryset = LoanApplication.objects.all().order_by('-created_at')

    @extend_schema(summary="Admin View All Loans", responses={200: LoanApplicationSerializer})
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminLoanUpdateView(generics.UpdateAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = LoanApplication.objects.all()
    lookup_field = 'pk'

    @extend_schema(summary="Admin Update Loan Status", request=LoanApplicationSerializer, responses={200: LoanApplicationSerializer})
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class AdminUserDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Users.objects.all()
    lookup_field = 'pk'

    @extend_schema(summary="Admin Delete User", responses={204: OpenApiResponse(description="User deleted successfully")})
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class AdminMakeSuperUserView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserProfileSerializer
    queryset = Users.objects.all()
    lookup_field = 'pk'

    @extend_schema(
        summary="Admin Make User Superuser",
        responses={200: OpenApiResponse(description="User promoted to superuser")}
    )
    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_superuser = True
        user.save()
        return JsonResponse({
            "message": "User successfully promoted to superuser.",
            "data": {"user_id": user.id, "email": user.email}
        }, status=200)
