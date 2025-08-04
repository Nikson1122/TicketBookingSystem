from django.urls import path
from .import views

urlpatterns = [

   path('', views.home_view, name='home'), 
   path('seat/', views.seat_view, name='seat_view'),
    path('vehicle/', views.veichle_view, name='vehicle_view'),
    path('vehicle/success/', views.vehicle_success, name='vehicle-success'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'), 
    path('vehicle/<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
     path('confirm-booking/', views.handle_booking, name='handle_booking'),
    
  


 

]
