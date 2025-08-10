from django import forms
from .models import Vehicle

class VehicleForm(forms.ModelForm):

    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    class Meta:  
        model = Vehicle
        fields = ['vehicle_type', 'vehicle_number', 'total_seats', 'departure_date', 'from_location', 'to_location', 'price']


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))


class BookingForm(forms.Form):
    vehicle_id = forms.IntegerField(widget=forms.HiddenInput)
    rental_type = forms.CharField(widget=forms.HiddenInput)
    price = forms.DecimalField(widget=forms.HiddenInput)
    quantity = forms.IntegerField(min_value=1, label='Hours/Days')