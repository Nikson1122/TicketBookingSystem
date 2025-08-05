from django.db import models
from django.utils import timezone

# Create your models here.




class Vehicle(models.Model):
    vehicle_type = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=15)
    departure_date = models.DateField(default=timezone.now)
    from_location = models.CharField(max_length=100,  default='Unknown')
    to_location= models.CharField(max_length=100, default='Unknown')
    total_seats = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    

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
    booked = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.seat_label} - {self.vehicle.vehicle_number}"



from django.db import models

class Bookings(models.Model):
    PAYMENT_CHOICES = [('esewa', 'eSewa'), ('khalti', 'Khalti')]

    seat_label = models.CharField(max_length=20)
    ticket_id = models.CharField(max_length=50)
    vehicle_id = models.CharField(max_length=50)
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    departure_date = models.DateField()
    email = models.EmailField()
    phonenumber = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    payment_status = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.ticket_id}"


