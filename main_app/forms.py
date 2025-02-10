from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Booking

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['package', 'booking_date', 'number_of_guests', 'total_price', 'contact_email', 'contact_phone']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'})
        }