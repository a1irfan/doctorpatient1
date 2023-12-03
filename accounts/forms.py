from django import forms
import datetime

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    phone_number = forms.CharField(max_length=15, required=True, label='Phone Number')  # Numeric field
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True,
                                 label='Birth Date')  # Date field
    #profile_picture = forms.ImageField(required=True, label='Profile Picture')


 # Custom validation for the phone_number field
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():  # Check if the input contains only digits
            raise forms.ValidationError("Invalid phone number. Please enter digits only.")
        return phone_number

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > datetime.date.today():
            raise forms.ValidationError("Birth date cannot be in the future.")
        return birth_date

