import ulid
from django.conf import settings
from django.db import models
from middlewares.user_middleware import get_current_user


def generate_ulid_as_string():
    return str(ulid.new())


class BaseModel(models.Model):
    id = models.CharField(primary_key=True, default=generate_ulid_as_string, editable=False, max_length=26)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_%(class)s",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="updated_%(class)s",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        if not self.pk:
            self.created_by = user
        self.updated_by = user
        super().save(*args, **kwargs)
