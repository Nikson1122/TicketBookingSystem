from django.shortcuts import render, redirect
from .models import Vehicle, Booking, Passenger, Payment, Seat
from .forms import VehicleForm
from django.http import HttpResponse

# Create your views here.

def home_view(request):
    return render(request, 'home.html') 



# def veichle_view(request):
#     if request.method == 'POST':
#         form = VehicleForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('vehicle-success')
#     else:
#         form = VehicleForm()  # 👈 this is now correctly handling GET

#     return render(request, 'ticket/vehicle_form.html', {'form': form})  # ✅ always returns


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

from django.shortcuts import render

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
    }

    return render(request, 'ticket/booking_confirmation.html', context)




