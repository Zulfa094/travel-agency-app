from django import forms
# from django.contrib.auth.forms import UserCreationForm
from .models import Booking

# class SignupForm(UserCreationForm):
#     # email = forms.EmailField(required=True)

#     class Meta(UserCreationForm.Meta):
#         fields = UserCreationForm.Meta.fields + ('email',)

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['package', 'booking_date']  
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'})
        }