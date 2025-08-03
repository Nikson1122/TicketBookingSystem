from django.db import models
from django.utils import timezone

# Create your models here.

class Passenger(models.Model):
    name =models.CharField(max_length=100)
    contact_number =models.CharField(max_length = 15)
    email = models.EmailField(blank=True, null=True)

def __str__(self):
    return self.name


class Vehicle(models.Model):
    vehicle_type = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=15)
    departure_date = models.DateField(default=timezone.now)
    From = models.CharField(max_length=100,  default='Unknown')
    To = models.CharField(max_length=100, default='Unknown')
    total_seats = models.IntegerField()
    

    def __str__(self):
        return f"{self.vehicle_type} - {self.vehicle_number}"

    def generate_seats(self):
        seat_labels = []
        seats_per_row = 4
        seat_letters = ['A', 'B', 'C', 'D']

        for i in range(self.total_seats):
            row = i // seats_per_row + 1
            col = i % seats_per_row
            seat_labels.append(f"{row}{seat_letters[col]}")

        return seat_labels

class Seat(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='seats')
    seat_label = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.seat_label} - {self.vehicle.vehicle_number}"

class Booking(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add = True)
    journey_date = models.DateField()
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
         return f"{self.passenger.name} - Seat {self.seat_number} on {self.journey_date}"
    


class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_gateway = models.CharField(max_length=50)  # e.g., Khalti, Esewa, Stripe
    transaction_id = models.CharField(max_length=100, unique=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.booking.passenger.name} - {self.amount} via {self.payment_gateway}"

