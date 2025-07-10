from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.utils import timezone
from django.http import JsonResponse
import datetime
from loan_app_backend.apps.loanapp.serializers import (
    RegistrationSerializer, LoginSerializer, ActivateUserSerializer, ForgotPasswordSerializer,
    ResetPasswordSerializer, UserProfileSerializer, UserProfileUpdateSerializer
)
from loan_app_backend.apps.loanapp.models import Users, ActivationCode
from loan_app_backend.apps.loanapp.emails import CustomActivationEmail
import random
import string


def generate_activation_code():
    return ''.join(random.choices(string.digits, k=6))


class RegisterUserView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Register User", request=RegistrationSerializer, responses={201: OpenApiResponse(description="Registration successful")})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({
                "message": "Validation failed.",
                "data": serializer.errors
            }, status=400)

        user = serializer.save()

        code = generate_activation_code()
        ActivationCode.objects.filter(user=user, purpose='activation').delete()
        ActivationCode.objects.create(user=user, code=code, purpose='activation', expires_at=timezone.now() + datetime.timedelta(minutes=5))

        CustomActivationEmail({'user': user, 'activation_code': code}).send([user.email])

        return JsonResponse({
            "message": "Registration successful. Please check your email to activate your account.",
            "data": {}
        }, status=201)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Login User", request=LoginSerializer, responses={200: OpenApiResponse(description="Login successful")})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({
                "message": "Validation failed.",
                "data": serializer.errors
            }, status=400)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        user_data = UserProfileSerializer(user).data
        user_data['is_superuser'] = user.is_superuser

        data = {
            'user': user_data,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'access_token_expiration': timezone.now() + refresh.access_token.lifetime,
            'refresh_token_expiration': timezone.now() + refresh.lifetime
        }

        return JsonResponse({
            "message": "User logged in successfully.",
            "data": data
        }, status=200)


class ActivateUserView(generics.GenericAPIView):
    serializer_class = ActivateUserSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Activate User", request=ActivateUserSerializer, responses={200: OpenApiResponse(description="User activated")})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({
                "message": "Validation failed.",
                "data": serializer.errors
            }, status=400)

        email = serializer.validated_data['email']
        resend_code = serializer.validated_data['resend_code']
        code = serializer.validated_data['code']
        user = Users.objects.get(email=email)

        if resend_code:
            ActivationCode.objects.filter(user=user, purpose='activation').delete()
            new_code = generate_activation_code()
            ActivationCode.objects.create(user=user, code=new_code, purpose='activation', expires_at=timezone.now() + datetime.timedelta(minutes=5))
            CustomActivationEmail({'user': user, 'activation_code': new_code}).send([email])
            return JsonResponse({"message": "New activation code sent.", "data": {}}, status=200)

        try:
            activation_code = ActivationCode.objects.get(user=user, code=code, purpose='activation')
        except ActivationCode.DoesNotExist:
            return JsonResponse({"message": "Invalid or expired activation code.", "data": {}}, status=400)

        if activation_code.is_expired():
            activation_code.delete()
            return JsonResponse({"message": "Activation code expired.", "data": {}}, status=400)

        user.is_active = True
        user.save()
        activation_code.delete()

        refresh = RefreshToken.for_user(user)

        user_data = UserProfileSerializer(user).data
        user_data['is_superuser'] = user.is_superuser

        return JsonResponse({
            "message": "User activated successfully.",
            "data": {
                "user": user_data,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "access_token_expiration": (timezone.now() + refresh.access_token.lifetime).isoformat(),
                "refresh_token_expiration": (timezone.now() + refresh.lifetime).isoformat(),
            }
        }, status=200)


class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Forgot Password", request=ForgotPasswordSerializer, responses={200: OpenApiResponse(description="Reset code sent")})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({
                "message": "Validation failed.",
                "data": serializer.errors
            }, status=400)
        email = serializer.validated_data['email']
        user = Users.objects.get(email=email)
        code = generate_activation_code()

        ActivationCode.objects.filter(user=user, purpose='reset').delete()
        ActivationCode.objects.create(user=user, code=code, purpose='reset', expires_at=timezone.now() + datetime.timedelta(minutes=5))

        CustomActivationEmail({'user': user, 'activation_code': code}).send([email])
        return JsonResponse({"message": "Password reset code sent to email.", "data": {}}, status=200)


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Reset Password", request=ResetPasswordSerializer, responses={200: OpenApiResponse(description="Password reset successful")})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({
                "message": "Validation failed.",
                "data": serializer.errors
            }, status=400)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        try:
            reset_code = ActivationCode.objects.get(user__email=email, code=code, purpose='reset')
        except ActivationCode.DoesNotExist:
            return JsonResponse({"message": "Invalid or expired reset code.", "data": {}}, status=400)

        if reset_code.is_expired():
            reset_code.delete()
            return JsonResponse({"message": "Reset code expired.", "data": {}}, status=400)

        user = reset_code.user
        user.set_password(new_password)
        user.save()
        reset_code.delete()

        return JsonResponse({"message": "Password reset successful.", "data": {}}, status=200)


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(
        summary="Get Current User Profile",
        responses={200: UserProfileSerializer}
    )
    def get(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(self.get_object())
        return JsonResponse({
            "message": "User profile fetched successfully.",
            "data": serializer.data
        }, status=200)

    @extend_schema(
        summary="Update User Profile",
        request=UserProfileUpdateSerializer,
        responses={
            200: OpenApiResponse(description="Profile updated successfully"),
            400: OpenApiResponse(description="Validation failed")
        }
    )
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return JsonResponse({
                "message": "Profile update failed.",
                "data": serializer.errors
            }, status=400)
        serializer.save()
        return JsonResponse({
            "message": "Profile updated successfully.",
            "data": serializer.data
        }, status=200)

    @extend_schema(
        summary="Delete User Profile",
        responses={204: OpenApiResponse(description="User profile deleted successfully")}
    )
    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return JsonResponse({
            "message": "User profile deleted successfully.",
            "data": {}
        }, status=204)
