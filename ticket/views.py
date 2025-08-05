from django.shortcuts import render, redirect
import requests 
from .models import Vehicle, Bookings, Seat
from .forms import VehicleForm
from django.http import HttpResponse
from datetime import datetime
from decimal import Decimal

from .utils.esewa import generate_esewa_signature
from django.conf import settings
import uuid
from django.db.models.functions import Upper



import base64
import json
from decimal import Decimal
from datetime import datetime
from django.shortcuts import render
from .models import Bookings
from django.shortcuts import render, get_object_or_404

# Create your views here.

def home_view(request):
    return render(request, 'home.html') 



def veichle_view(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()

            # Generate and save seats
            seat_labels = vehicle.generate_seats()
            Seat.objects.bulk_create([
                Seat(vehicle=vehicle, seat_label=label)
                for label in seat_labels
            ])

            return redirect('vehicle-success')
    else:
        form = VehicleForm()
    return render(request, 'ticket/vehicle_form.html', {'form': form})


def vehicle_success(request):
    return HttpResponse("Vehicle saved successfully!")

def seat_view(request):
    seat_layout = {
        "row1": ['1a'],
        "driver": "Driver",
        "row2": ['2a', '2b', '2c'],
        "row3": ['3a', '3b', '3c'],
    }
    booked = ['2b', '3a']  
    return render(request, 'ticket/seat.html', {'seat_layout': seat_layout, 'booked': booked})




def vehicle_list(request):
    vehicles = Vehicle.objects.all()

    from_value = request.GET.get('from_location')
    to_value = request.GET.get('to_location')
    date_value = request.GET.get('departure_date')

    if from_value:
        vehicles = vehicles.filter(from_location__icontains=from_value)
    if to_value:
        vehicles = vehicles.filter(to_location__icontains=to_value)
    if date_value:
        vehicles = vehicles.filter(departure_date=date_value)

    from_options = Vehicle.objects.values_list('from_location', flat=True).distinct()
    to_options = Vehicle.objects.values_list('to_location', flat=True).distinct()

    context = {
        'vehicles': vehicles,
        'from_value': from_value,
        'to_value': to_value,
        'date_value': date_value,
        'from_options': from_options,
        'to_options': to_options,
    }

    return render(request, 'ticket/vehicle_list.html', context)


def vehicle_detail(request, vehicle_id):
    vehicle = Vehicle.objects.get(id=vehicle_id)
    seats = vehicle.seats.all() 

    return render(request, 'ticket/vehiclelist.html', {
        'vehicle': vehicle,
        'seats': seats,
    })


def handle_booking(request):
    # Get the GET parameters
    seat_label = request.GET.get('seatLabel', '')
    ticket_id = request.GET.get('ticketId', '')
    vehicle_id = request.GET.get('vehicleId', '')
    from_location = request.GET.get('from', '')
    to_location = request.GET.get('to', '')
    departure_date = request.GET.get('departureDate', '')
    email = request.GET.get('email', '')  # User's email, just for reference
    phonenumber = request.GET.get('phonenumber', '')  
    name = request.GET.get('name', '')
    price = request.GET.get('price', '')

    context = {
        'seat_label': seat_label,
        'ticket_id': ticket_id,
        'vehicle_id': vehicle_id,
        'from_location': from_location,
        'to_location': to_location,
        'departure_date': departure_date,
        'email': email,
        'phonenumber': phonenumber,
        'name': name,
        'price': price,
    }

    return render(request, 'ticket/booking_confirmation.html', context)


def initiate_esewa_payment(request):
    # Get booking details from POST
    price = request.POST.get('price')
    ticket_id = request.POST.get('ticket_id')
    seat_label = request.POST.get('seat_label')
    vehicle_id = request.POST.get('vehicle_id')
    from_location = request.POST.get('from_location')
    to_location = request.POST.get('to_location')
    departure_date = request.POST.get('departure_date')
    email = request.POST.get('email')
    phonenumber = request.POST.get('phonenumber')
    name = request.POST.get('name')

    transaction_uuid = str(uuid.uuid4())
    signature = generate_esewa_signature(price, transaction_uuid)

    success_url = request.build_absolute_uri('/esewa/success/')
    failure_url = request.build_absolute_uri('/esewa/failure/')

    # ✅ Store all booking data in session
    request.session['booking_data'] = {
        'price': price,
        'ticket_id': ticket_id,
        'seat_label': seat_label,
        'vehicle_id': vehicle_id,
        'from_location': from_location,
        'to_location': to_location,
        'departure_date': departure_date,  # Must be a string like "2025-08-05"
        'email': email,
        'phonenumber': phonenumber,
        'name': name,
        'transaction_uuid': transaction_uuid
    }

    context = {
        'amount': price,
        'tax_amount': '0',
        'total_amount': price,
        'transaction_uuid': transaction_uuid,
        'product_code': settings.ESEWA_MERCHANT_CODE,
        'product_service_charge': '0',
        'product_delivery_charge': '0',
        'success_url': success_url,
        'failure_url': failure_url,
        'signed_field_names': 'total_amount,transaction_uuid,product_code',
        'signature': signature,
    }
    return render(request, 'ticket/esewa.html', context)





def esewa_success(request):
    print("✅ [DEBUG] eSewa success view called")

    # 1. Decode the 'data' from eSewa
    data_encoded = request.GET.get('data')
    try:
        data_json = base64.b64decode(data_encoded).decode('utf-8')
        data = json.loads(data_json)
        print("[DEBUG] Decoded eSewa data:", data)
    except Exception as e:
        print("[ERROR] Could not decode eSewa data:", e)
        return render(request, 'ticket/esewasucess.html', {'error': 'Payment verification failed.'})

    # 2. Get booking data from session
    booking_data = request.session.get('booking_data', {})
    print("[DEBUG] Booking data from session:", booking_data)

    transaction_id = data.get('transaction_code')
    ticket_id = booking_data.get('ticket_id')
    seat_label = booking_data.get('seat_label')
    vehicle_id = booking_data.get('vehicle_id')
    from_location = booking_data.get('from_location')
    to_location = booking_data.get('to_location')
    departure_date_str = booking_data.get('departure_date')
    
    try:
        departure_date = datetime.strptime(departure_date_str, '%b. %d, %Y').date()
    except (ValueError, TypeError) as e:
        print(f"[ERROR] Invalid departure date (format %b. %d, %Y): {e}")
        try:
            # Try an alternative format if the first one fails
            departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d').date()
        except Exception as e:
            print("[ERROR] Invalid departure date (format %Y-%m-%d):", e)
            departure_date = None

    email = booking_data.get('email')
    phonenumber = booking_data.get('phonenumber')
    name = booking_data.get('name')
    price_str = booking_data.get('price')

    try:
        price = Decimal(price_str)
    except Exception as e:
        print("[ERROR] Invalid price:", e)
        price = Decimal('0.00')

    # Save booking if all required data is valid
    if transaction_id and departure_date:
        try:
            booking = Bookings.objects.create(
                seat_label=seat_label,
                ticket_id=ticket_id,
                vehicle_id=vehicle_id,
                from_location=from_location,
                to_location=to_location,
                departure_date=departure_date,
                email=email,
                phonenumber=phonenumber,
                name=name,
                price=price,
                payment_method='esewa',
                payment_status=True,
                transaction_id=transaction_id
            )
            print("[SUCCESS] Booking saved:", booking)
        except Exception as e:
            print("[ERROR] Failed to save booking:", e)
    else:
        print("[ERROR] Required fields missing. Booking not saved.")

    return render(request, 'ticket/esewasucess.html', {'ticket_id': ticket_id})





def seat_selection_view(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    # Get seats for vehicle
    seats = Seat.objects.filter(vehicle=vehicle).order_by('seat_label')

    # Get booked seat labels for this vehicle with payment done
    booked_labels_qs = Bookings.objects.filter(
        vehicle_id=vehicle.id,
        payment_status=True
    ).values_list('seat_label', flat=True)

    # Normalize to uppercase
    booked_seat_labels = set(label.upper() for label in booked_labels_qs if label)

    context = {
        'vehicle': vehicle,
        'seats': seats,
        'booked_seat_labels': booked_seat_labels,
    }
    return render(request, 'ticket/vehiclelist.html', context)