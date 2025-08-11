from django.shortcuts import render, redirect
import requests 
from .models import Vehicle, Bookings, Seat
from .forms import VehicleForm, BookingForm 
from django.http import HttpResponse
from datetime import datetime
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib import messages
from .forms import LoginForm
import json
from django.http import JsonResponse
from .utils.esewa import generate_esewa_signature
from django.conf import settings
import uuid
from django.db.models.functions import Upper
from django.views.decorators.http import require_POST
import threading
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.utils.timezone import now


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


    data_encoded = request.GET.get('data')
    try:
        data_json = base64.b64decode(data_encoded).decode('utf-8')
        data = json.loads(data_json)
        print("[DEBUG] Decoded eSewa data:", data)
    except Exception as e:
        print("[ERROR] Could not decode eSewa data:", e)
        return render(request, 'ticket/esewasucess.html', {'error': 'Payment verification failed.'})

  
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

    
    booked_labels_qs = Bookings.objects.filter(
        vehicle_id=vehicle.id,
        payment_status=True
    ).values_list('seat_label', flat=True)

    
    booked_seat_labels = set(label.upper() for label in booked_labels_qs if label)

    context = {
        'vehicle': vehicle,
        'seats': seats,
        'booked_seat_labels': booked_seat_labels,
    }
    return render(request, 'ticket/vehiclelist.html', context)








def fetch_vehicles(request):
    try:
        response = requests.get('http://localhost:8080/inventory/webresources/generic/vehicles')
        response.raise_for_status()
        vehicles = response.json()
    except requests.exceptions.RequestException as e:
        vehicles = []
        print("Error fetching data:", e)

    total_price = None
    selected_vehicle_id = None

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            rental_type = form.cleaned_data['rental_type']
            price = form.cleaned_data['price']
            print("price is", price)

            selected_vehicle_id = request.POST.get('vehicle_id')
        vehicle_number = None

        # Debug print
        print(f"Selected vehicle ID from form: {selected_vehicle_id}")

        
        if selected_vehicle_id:
            for v in vehicles:
                if str(v.get('id')) == str(selected_vehicle_id):
                    vehicle_number = v.get('veichleNumber')
                    print(f"Vehicle number found: {vehicle_number}")
                    break
          
     
            total_price = quantity * price
            request.session['total_price'] = float(total_price)
            request.session['rental_type'] = rental_type
            request.session['vehicle_number'] = vehicle_number

            request.session['vehicle_id'] = int(selected_vehicle_id) if selected_vehicle_id else None

            
            selected_vehicle_id = int(selected_vehicle_id) if selected_vehicle_id else None
            
            return render(request, 'ticket/vechileapi.html', {
                'vehicles': vehicles,
                'form': form,
                'total_price': total_price,
                'selected_vehicle_id': selected_vehicle_id,
                'show_result': True
            })
    else:
        form = BookingForm()  

    return render(request, 'ticket/vechileapi.html', {
        'vehicles': vehicles,
        'form': form
    })






JAVA_API_LOGIN_URL = "http://localhost:8080/inventory/webresources/generic/login"

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            payload = json.dumps({'email': email, 'password': password})
            headers = {'Content-Type': 'text/plain'}

            try:
                response = requests.post(JAVA_API_LOGIN_URL, data=payload, headers=headers)

                print("API Response status:", response.status_code)
                print("API Response body:", response.text)

                if response.status_code == 200:
                    json_data = response.json()
                    token = json_data.get('token')
                    if token:
                        request.session['jwt_token'] = token
                        return redirect('fetch_vehicles')  
                    else:
                        messages.error(request, "Login failed: No token received from server.")
                elif response.status_code == 401:
                    messages.error(request, "Invalid credentials.")
                else:
                    messages.error(request, f"Login failed with status code {response.status_code}.")
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Error contacting authentication server: {e}")
    else:
        form = LoginForm()

    return render(request, 'home.html', {'form': form})



def esewa_book(request):
  
    total_price = request.session.get('total_price', None)
    print("Total price from session:", total_price)
    if total_price is None:

        pass

 
    transaction_uuid = str(uuid.uuid4())


    signature = generate_esewa_signature(total_price, transaction_uuid)

    success_url = request.build_absolute_uri('/esewa/success/')
    failure_url = request.build_absolute_uri('/esewa/failure/')

    context = {
        'amount': total_price,
        'tax_amount': '0',
        'total_amount': total_price,
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




def initiate_khalti_payment(request):
    total_price = request.session.get('total_price', None)
    print("Total price from session:", total_price)
    if not total_price:
        print("No total price found in session")
        return redirect('vehicle_list')  

    transaction_uuid = str(uuid.uuid4())

    try:
        url = "https://dev.khalti.com/api/v2/epayment/initiate/"

        headers = {
            "Authorization": "key live_secret_key_68791341fdd94846a146f0457ff7b455",
            "Content-Type": "application/json"
        }

        amount_in_paisa = int(float(total_price) * 100)

        payload = {
            "return_url": "http://127.0.0.1:8000/khalti/verify",

            "website_url": "http://127.0.0.1:8000/vnumber/",
            "amount": str(amount_in_paisa),
            "purchase_order_id": transaction_uuid,
            "purchase_order_name": f"Booking Order {transaction_uuid}" 
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            data = response.json()
            payment_url = data.get("payment_url")
            pidx = data.get("pidx")

            print("pidx:", pidx)
            print("payment_url:", payment_url)
            print("Khalti Response:", data)

         
            request.session['khalti_pidx'] = pidx

     
            return redirect(payment_url)
        else:
            print("Error:", response.status_code, response.text)
            return redirect('payment_failed')

    except Exception as e:
        print("Exception occurred:", e)
        return redirect('payment_failed')





# Define this once outside the view
def verify_payment(pidx):
    secret_key = "key live_secret_key_68791341fdd94846a146f0457ff7b455"
    endpoint = "https://dev.khalti.com/api/v2/epayment/lookup/"

    headers = {
        "Authorization": secret_key,
        "Content-Type": "application/json"
    }

    json_data = {
        "pidx": pidx
    }

    try:
        response = requests.post(endpoint, json=json_data, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        print("Khalti Lookup Response:", json_response)
        status_completed = json_response.get("status") == "Completed"
        print("Is payment completed?", status_completed)
        return status_completed, json_response  
    except requests.RequestException as e:
        print("Error verifying Khalti payment:", e)
        return False, {}
    

def call_save_payment_async(payment_data, save_payment_url):
    try:
        response = requests.post(save_payment_url, json=payment_data, timeout=5)
        print("Save Payment Response:", response.status_code, response.text)
    except Exception as e:
        print(f"Error calling save payment: {e}")

def verify_khalti_payment(request):
    pidx = request.GET.get('pidx')

    if not pidx:
        return JsonResponse({'error': 'pidx parameter missing'}, status=400)

    payment_completed, khalti_response = verify_payment(pidx)
    booking_date = now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    # payment_data = {
    #     "amount": khalti_response.get("total_amount"),
    #     "transactionId": khalti_response.get("transaction_id"),
    #     "paymentMethod": "khalti",
    # }

    payment_data = {
    "price": str(request.session.get("total_price")),
    "transactionUUID": khalti_response.get("transaction_id"),
    "veichleNumber": request.session.get("vehicle_number"),
    "rentalType": request.session.get("rental_type"),
    "bookingDate": booking_date,
    "user": {
        "id": request.user.id  
    }
}

    
    save_payment_url = request.build_absolute_uri('/save-payment/')

    threading.Thread(target=call_save_payment_async, args=(payment_data, save_payment_url)).start()

    return JsonResponse({
        'payment_completed': payment_completed,
        'khalti_response': khalti_response
    })


    



@csrf_exempt
def save_payment(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed")

    try:
        payment_data = json.loads(request.body)

        url = "http://localhost:8080/inventory/webresources/generic/payment"
        response = requests.post(url, json=payment_data)
        response.raise_for_status()

        return JsonResponse({"message": "Payment saved successfully"}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

