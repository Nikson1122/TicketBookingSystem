from django.contrib import admin
from django.contrib import admin
from .models import  Vehicle,Bookings


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_type', 'vehicle_number', 'total_seats')



@admin.register(Bookings)
class BookingsAdmin(admin.ModelAdmin):
    list_display = ('name','email','phonenumber',   'seat_label','ticket_id', 'vehicle_id', 'from_location', 'to_location', 'departure_date', 'price', 'payment_method', 'payment_status', 'created_at',)
    list_filter = ('departure_date', 'payment_method', 'payment_status')
    search_fields = ('name', 'ticket_id', 'vehicle_id', 'email', 'phonenumber')