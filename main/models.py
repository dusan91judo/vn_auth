import uuid
from django.db import models
from django.db.models import JSONField
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser


class UserManager(BaseUserManager):
    """Custom user model manager without username field."""

    use_in_migrations = True

    def get_by_natural_key(self, username):
        return self.get(email__iexact=username)

    def get_queryset(self):
        """Filter out 'soft deleted' records."""
        return super().get_queryset().filter(deleted_at__isnull=True)

    def _create_user(self, email, password, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')

        email = email.lower()  # Make entire email address lowercase.
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a standard user with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class SoftDeleteManager(models.Manager):
    """Override the base queryset to Filter out 'soft deleted' records"""

    def get_queryset(self):
        """Filter out 'soft deleted' records."""
        return super().get_queryset().filter(deleted_at__isnull=True)


class BaseModel(models.Model):
    """Base model for mandatory fields on all models."""
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, editable=False)

    class Meta:
        abstract = True


class BaseModelSoftDelete(BaseModel):
    """
    Extend the base model to add 'soft deletion'

    It overrides the base manager & queryset for all it's children
    i.e Model.objects.all() filters out all 'soft deleted' records
    Model.all_objects.all() returns all records including the deleted records.
    """

    # Override base queryset
    objects = SoftDeleteManager()

    # Return all objects including soft deleted objects
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """Soft delete an object."""
        self.deleted_at = timezone.now()
        self.save()

    def force_delete(self, *args, **kwargs):
        """Force delete an object."""
        super().delete(*args, **kwargs)


class User(AbstractUser, BaseModelSoftDelete):
    """Custom user model to add extra fields to Django's user model."""

    # Use a custom manager.
    objects = UserManager()

    # Disable the username field.
    username = None

    # Set email as the username field.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email = models.EmailField(  # Redefine email field.
        'email address',
        unique=True,
        error_messages={
            'unique': 'A user with this email address already exists.',
        },
    )
    picture = StorageImageField('Profile picture', default=settings.BUCKET_USERIMAGES.split('/', 1)[-1] + '/User.png', bucket_path=settings.BUCKET_USERIMAGES)  # noqa
    show_onboarding = models.BooleanField(default=True)
    attrs = JSONField(default={}, max_length=5000, blank=True)
