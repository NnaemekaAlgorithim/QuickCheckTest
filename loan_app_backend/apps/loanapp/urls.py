from django.urls import path
from loan_app_backend.apps.loanapp.views.admin_views import (
    AdminLoanListView,
    AdminLoanUpdateView,
    AdminMakeSuperUserView,
    AdminUserDeleteView,
    AdminUserListView
)
from loan_app_backend.apps.loanapp.views.loan_request import (
    LoanApplicationView
)
from loan_app_backend.apps.loanapp.views.login_registration import (
    RegisterUserView, LoginView, ActivateUserView,
    ForgotPasswordView, ResetPasswordView, UserProfileView
)

urlpatterns = [
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/activate/', ActivateUserView.as_view(), name='activate-user'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('loans/', LoanApplicationView.as_view(), name='loan-application'),
    path("admin/users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("admin/users/<str:id>/delete/", AdminUserDeleteView.as_view(), name="admin-user-delete"),
    path("admin/users/<str:id>/make-superuser/", AdminMakeSuperUserView.as_view(), name="admin-user-make-superuser"),
    path("admin/loans/", AdminLoanListView.as_view(), name="admin-loan-list"),
    path("admin/loans/<str:id>/update/", AdminLoanUpdateView.as_view(), name="admin-loan-update"),
]
