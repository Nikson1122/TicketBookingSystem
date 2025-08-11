from django.urls import path
from .import views

urlpatterns = [

   path('', views.login_view, name='login'), 
   path('seat/', views.seat_view, name='seat_view'),
    path('vehicle/', views.veichle_view, name='vehicle_view'),
    path('vehicle/success/', views.vehicle_success, name='vehicle-success'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'), 
    path('vehicle/<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
     path('confirm-booking/', views.handle_booking, name='handle_booking'),
        path('esewa/initiate/', views.initiate_esewa_payment, name='esewa_initiate'),
    path('esewa/success/', views.esewa_success, name='esewa_success'),
    path('vehicles/<int:vehicle_id>/seats/', views.seat_selection_view, name='seat_selection'),
    path('vnumber/', views.fetch_vehicles, name='fetch_vehicles'),
    path('book/', views.esewa_book, name='esewa_book'),
    path('khalti/', views. initiate_khalti_payment, name='khalti_book'),
  

    # path('login/', views.login_view, name='login'),
  

    # path('book/', views.book_seat, name='book_seat'),
  
    
  


 

]
