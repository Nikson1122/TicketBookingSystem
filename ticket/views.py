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
    return render(request, 'ticket/vehicle_list.html', {'vehicles': vehicles})


def vehicle_detail(request, vehicle_id):
    vehicle = Vehicle.objects.get(id=vehicle_id)
    seats = vehicle.seats.all() 

    return render(request, 'ticket/vehiclelist.html', {
        'vehicle': vehicle,
        'seats': seats,
    })


