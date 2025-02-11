from django import forms
# can you make 
from .models import Booking, Package

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

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['name', 'description', 'price', 'destinations']