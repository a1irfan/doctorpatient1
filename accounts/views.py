from django.shortcuts import render
from django.http import HttpResponse
from .forms import ContactForm
from rest_framework import generics
from .models import CustomUser, Doctor, Patient, DoctorPrescription
from .serializers import CustomUserSerializer, DoctorSerializer, PatientSerializer, DoctorPrescriptionSerializer
#NEW PACKAGES
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from payments.models import StripeCustomer
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required




@login_required
def logout_view(request):
    logout(request)
    return redirect('/')
def mypage(request):
    return HttpResponse("Hello this is my first view!")

def home(request):
    return render(request, 'index.html', context={})
def login(request):
    return render(request, 'login.html', context={})
def doctor_signup(request):
    return render(request, 'signup_doctor.html', context={})
def patient_signup(request):
    return render(request, 'signup_patient.html', context={})
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            # Here you can do something with the form data like saving it to the database
            # For now, let's just display a thank you message
            return render(request, 'thank_you.html', {'name': name, 'email':email, 'msg':message})
    else:
        form = ContactForm()

    return render(request, 'contact_form.html', {'form': form})

# API FOR CREATE USER, DELETE USER, UPDATE USER, GET USER AND GET ALL USERS

class CustomUserListCreateAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class CustomUserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

@api_view(['POST'])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, email=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        package = False
        if user.role == 1:
            try:
                StripeCustomer.objects.get(doctor=user.id)
                package = True
                print(True)

            except StripeCustomer.DoesNotExist:
                package = False
                print(False)

        #return Response({'access_token': access_token}, status=status.HTTP_200_OK)

        return Response({'access_token': access_token, 'role': user.role, 'user_id': user.id, 'package':package,}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class DoctorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DoctorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

# PATIENT API BELOW

class PatientListCreateAPIView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PatientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        patient = get_object_or_404(Patient, user_id=user_id)
        self.check_object_permissions(self.request, patient)
        return patient

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)



class PatientPrescriptionListCreateAPIView(generics.ListCreateAPIView):
    queryset = DoctorPrescription.objects.all()
    serializer_class = DoctorPrescriptionSerializer

    def perform_create(self, serializer):
        doctor_id = self.request.data.get('doctor')
        patient_id = self.request.data.get('patient')

        # Check if doctor and patient exist in the database
        doctor_exists = Doctor.objects.filter(user_id=doctor_id).exists()
        patient_exists = Patient.objects.filter(user_id=patient_id).exists()

        if not doctor_exists or not patient_exists:
            return Response({"error": "Doctor and/or patient does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()


class PatientPrescriptionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorPrescriptionSerializer

    def get_object(self):
        patient_id = self.kwargs.get('patient')
        print("HELLO",patient_id)
        prescription = get_object_or_404(DoctorPrescription, patient=patient_id)
        self.check_object_permissions(self.request, prescription)
        return prescription

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


