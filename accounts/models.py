from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from datetime import datetime
import random
import string

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, role, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, role=role)
        user.set_password(password)
        user.date_of_joining = datetime.now()  # Set date_of_joining to current date and time
        user.save(using=self._db)
        return user


    def create_superuser(self, email, username, password=None):
        user = self.create_user(email, username, role=3, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        (1, 'Doctor'),
        (2, 'Patient'),
        (3, 'Admin'),
    )
    email = models.EmailField(unique=True, null=False)
    username = models.CharField(max_length=100, unique=True)
    role = models.IntegerField(choices=ROLES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_of_joining = models.DateField(auto_now_add=True)  # Set date_of_joining to current date and time automatically

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

def generate_referral_id():
    return ''.join(random.choices(string.digits, k=10))  # Generates a random 10-digit string

class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    referral_id = models.CharField(max_length=10, unique=True, default=generate_referral_id)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    #profile_image = models.ImageField(upload_to='doctor_profiles/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    doctor_referral_id = models.CharField(max_length=10)  # Referral ID of the corresponding doctor
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    #profile_image = models.ImageField(upload_to='patient_profiles/', null=True, blank=True)
    nic = models.CharField(max_length=15)
    # Other patient-specific fields

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class DoctorPrescription(models.Model):
    doctor = models.IntegerField(null=False, blank=False)
    patient = models.IntegerField(null=False, blank=False)
    issue_description = models.TextField()
    prescription_text = models.TextField()
    next_visit_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient}"