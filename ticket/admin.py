from django.contrib import admin
from django.contrib import admin
from .models import Passenger, Vehicle, Booking, Payment, Bookings

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_number', 'email')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_type', 'vehicle_number', 'total_seats')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('passenger', 'vehicle', 'journey_date', 'is_confirmed')
    list_filter = ('is_confirmed', 'journey_date')
    search_fields = ('passenger__name', 'vehicle__vehicle_number')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'payment_gateway', 'transaction_id', 'is_successful', 'paid_at')
    list_filter = ('payment_gateway', 'is_successful')
    search_fields = ('transaction_id',)

@admin.register(Bookings)
class BookingsAdmin(admin.ModelAdmin):
    list_display = ('name','email','phonenumber','ticket_id', 'vehicle_id', 'from_location', 'to_location', 'departure_date', 'price', 'payment_method', 'payment_status', 'created_at',)
    list_filter = ('departure_date', 'payment_method', 'payment_status')
    search_fields = ('name', 'ticket_id', 'vehicle_id', 'email', 'phonenumber')