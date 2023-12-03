from rest_framework import serializers
from .models import CustomUser, Doctor, Patient, DoctorPrescription
from django.shortcuts import get_object_or_404
import datetime

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'role', 'password')
        extra_kwargs = {'password': {'write_only': True}}  # Ensures password is write-only field

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            role=validated_data['role'],
            password=validated_data['password']
        )
        return user

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('id', 'referral_id', 'first_name', 'last_name', 'dob', 'profile_image')
        read_only_fields = ('id', 'referral_id')

    def validate_dob(self, value):
        # Custom validation for 'dob' field
        # Example: Check if the date of birth is in the past
        if value and value > datetime.date.today():
            raise serializers.ValidationError("Date of birth must be in the past.")
        return value
    def create(self, validated_data):
        """
        Create a new Doctor instance with the validated data.
        """
        # Extract the 'profile_image' data from the validated data
        profile_image_data = validated_data.pop('profile_image', None)

        # Create a new Doctor instance without the 'profile_image'
        doctor = Doctor.objects.create(**validated_data)

        # If 'profile_image' data exists, set it separately
        if profile_image_data:
            doctor.profile_image = profile_image_data
            doctor.save()

        return doctor

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'doctor_referral_id', 'first_name', 'last_name', 'dob', 'nic')

    def validate_doctor_referral_id(self, value):
        try:
            doctor = Doctor.objects.get(referral_id=value)
        except Doctor.DoesNotExist:
            raise serializers.ValidationError('Invalid referral ID. No doctor found with this ID.')
        return value





class DoctorPrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorPrescription
        fields = ('id', 'doctor', 'patient', 'issue_description', 'prescription_text', 'next_visit_date', 'created_at')
        read_only_fields = ('id', 'created_at')
