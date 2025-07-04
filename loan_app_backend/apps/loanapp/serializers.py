import uuid
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import MinLengthValidator
from django.contrib.auth.password_validation import validate_password
from loan_app_backend.apps.loanapp.models import LoanApplication, Users


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[MinLengthValidator(8)])
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = Users
        fields = ('first_name', 'last_name', 'email', 'password')

    def validate_email(self, value):
        if Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def create(self, validated_data):
        # Generate a unique username
        while True:
            random_username = f"user_{uuid.uuid4().hex[:8]}"
            if not Users.objects.filter(username=random_username).exists():
                break

        validated_data["username"] = random_username
        user = Users.objects.create_user(**validated_data, is_active=False)
        return user


class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email_or_username = data.get('email_or_username')
        password = data.get('password')

        user = None

        # Try email first
        if Users.objects.filter(email=email_or_username).exists():
            user = Users.objects.get(email=email_or_username)
        elif Users.objects.filter(username=email_or_username).exists():
            user = Users.objects.get(username=email_or_username)
        else:
            raise serializers.ValidationError({'detail': 'Invalid email/username or password.'})

        if not user.is_active:
            raise serializers.ValidationError({'detail': 'Account not activated.'})

        # Authenticate with username or email (depending on what was found)
        login_key = user.email if Users.USERNAME_FIELD == "email" else user.username
        authenticated_user = authenticate(
            request=self.context.get('request'),
            username=login_key,
            password=password
        )

        if not authenticated_user:
            raise serializers.ValidationError({'detail': 'Invalid email/username or password.'})

        data['user'] = authenticated_user
        return data


class ActivateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    resend_code = serializers.BooleanField(default=False)

    def validate_email(self, value):
        if not Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active']
        read_only_fields = ['id', 'username', 'role', 'is_active']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[MinLengthValidator(8)])

    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'password']

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = ['id', 'amount_requested', 'purpose', 'status']
        read_only_fields = ['status']
