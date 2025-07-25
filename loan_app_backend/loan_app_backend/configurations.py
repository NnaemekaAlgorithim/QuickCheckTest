from decouple import config, Csv

# Basic settings
BASE_PREFIX = config('BASE_PREFIX', default='')
DEBUG = config('DEBUG', default=True, cast=bool)
SECRET_KEY = config('SECRET_KEY', default='')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1', cast=Csv())
EMAIL_BACKEND = config('EMAIL_BACKEND', default='')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='')
SOCIAL_AUTH_FACEBOOK_SCOPE = config('SOCIAL_AUTH_FACEBOOK_SCOPE', default='')
SOCIAL_AUTH_FACEBOOK_SECRET = config('SOCIAL_AUTH_FACEBOOK_SECRET', default='')
SOCIAL_AUTH_FACEBOOK_KEY = config('SOCIAL_AUTH_FACEBOOK_KEY', default='')
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', default='')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', default='')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = config('SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE', default='')
ENABLE_SOCIAL_AUTH = config('ENABLE_SOCIAL_AUTH', default=False)
CLOUDINARY_CLOUD_NAME = config('CLOUDINARY_CLOUD_NAME', default='')
CLOUDINARY_API_KEY = config('CLOUDINARY_API_KEY', default='')
CLOUDINARY_API_SECRET = config('CLOUDINARY_API_SECRET', default='')
DB_HOST_NAME = config('DB_HOST_NAME', default='')
DB_PORT = config('DB_PORT', default='')
DB_NAME = config('DB_NAME', default='')
DB_USER_NAME = config('DB_USER_NAME', default='')
DB_PASSWORD = config('DB_PASSWORD', default='')
DATABASE_URL=f'postgresql://{DB_USER_NAME}:{DB_PASSWORD}@{DB_HOST_NAME}/{DB_NAME}'
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
