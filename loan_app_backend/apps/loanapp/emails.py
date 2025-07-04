from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


class CustomActivationEmail:
    html_email_template_name = "email_templates/user_activation.html"

    def __init__(self, context):
        self.context = context

    def send(self, to):
        subject = "Activate Your LoanApp Account"
        html_message = render_to_string(self.html_email_template_name, self.context)
        from_email = settings.DEFAULT_FROM_EMAIL

        send_mail(
            subject,
            '', #  Plain text message (not used here)
            from_email,
            to,
            html_message=html_message,
            fail_silently=False,
        )


class BlockedUserEmail:
    html_email_template_name = "email_templates/user_blocked.html"

    def __init__(self, context):
        self.context = context

    def send(self, to):
        subject = "LoanApp Account Blocked"
        html_message = render_to_string(self.html_email_template_name, self.context)
        from_email = settings.DEFAULT_FROM_EMAIL

        send_mail(
            subject,
            '',  # Plain text message (not used here)
            from_email,
            to,
            html_message=html_message,
            fail_silently=False,
        )


class UnblockedUserEmail:
    html_email_template_name = "email_templates/user_unblocked.html"

    def __init__(self, context):
        self.context = context

    def send(self, to):
        subject = "LoanApp Account Unblocked"
        html_message = render_to_string(self.html_email_template_name, self.context)
        from_email = settings.DEFAULT_FROM_EMAIL

        send_mail(
            subject,
            '',  # Plain text message (not used here)
            from_email,
            to,
            html_message=html_message,
            fail_silently=False,
        )


class PasswordResetEmail:
    html_email_template_name = "email_templates/password_reset.html"

    def __init__(self, context):
        self.context = context

    def send(self, to):
        subject = "Reset Your LoanApp Password"
        html_message = render_to_string(self.html_email_template_name, self.context)
        from_email = settings.DEFAULT_FROM_EMAIL

        send_mail(
            subject,
            '',  # Empty plain text version
            from_email,
            to,
            html_message=html_message,
            fail_silently=False,
        )


def send_email(subject, message, recipient_list, from_email=None, fail_silently=False):
    """
    Send a plain text email using Django's configured backend.

    Args:
        subject (str): Email subject line.
        message (str): Plain text email body.
        recipient_list (list): List of recipient email addresses.
        from_email (str, optional): Sender email. Defaults to settings.DEFAULT_FROM_EMAIL.
        fail_silently (bool, optional): If True, suppress email send errors. Defaults to False.
    """
    from_email = from_email or settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, recipient_list, fail_silently=fail_silently)
