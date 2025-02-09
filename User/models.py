from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from cloudinary.models import CloudinaryField
from Domain.models import Domain
from django.core.exceptions import ValidationError



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

def validate_akgec_email(value):
        if not value.endswith('@akgec.ac.in'):
            raise ValidationError("Email must end with '@akgec.ac.in'.")

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('banned', 'Banned'),
    ]

    YEAR_CHOICES = [
        ('2nd', '2nd Year'),
        ('3rd', '3rd Year'),
        ('4th', '4th Year'),
    ]

    email = models.EmailField(unique=True, validators=[validate_akgec_email])
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    photo = CloudinaryField('image', blank=True, null=True)
    domain = models.ForeignKey(Domain, on_delete=models.SET_NULL, null=True)
    linkedin_url = models.URLField(max_length=200, blank=True, null=True)
    insta_url = models.URLField(max_length=200, blank=True, null=True)
    github_url = models.URLField(max_length=200, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    bio = models.TextField()
    year = models.CharField(max_length=10, choices=YEAR_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_staff = models.BooleanField(default=False)  # Required for admin interface
    is_active = models.BooleanField(default=True)  # Required for authentication
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role', 'year']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

