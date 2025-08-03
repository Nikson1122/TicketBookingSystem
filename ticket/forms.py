from django import forms
from .models import Vehicle

class VehicleForm(forms.ModelForm):

    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    class Meta:  
        model = Vehicle
        fields = ['vehicle_type', 'vehicle_number', 'total_seats', 'departure_date', 'from_location', 'to_location']
