"""
WSGI config for loan_app_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from loan_app_backend.loan_app_backend.configurations import DEBUG

from django.core.wsgi import get_wsgi_application

if DEBUG:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "loan_app_backend.loan_app_backend.settings.dev_settings")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "loan_app_backend.loan_app_backend.settings.prod_settings")

application = get_wsgi_application()
