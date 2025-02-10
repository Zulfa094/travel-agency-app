from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "main_app"

urlpatterns = [
    path('', views.Home.as_view(), name='home'),  # Use built-in login view
    path('about/', views.about, name='about'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'), #login path

    # CBV's for Create, Update, Delete Package
    path('packages/create/', views.PackageCreate.as_view(), name='package_create'),
    path('packages/<int:pk>/update', views.PackageUpdate.as_view(), name='package_update'),
    path('packages/<int:pk>/delete', views.PackageDelete.as_view(), name='package_delete'),
    path('packages/<int:pk>', views.PackageDetail.as_view(), name='package_detail'),

        # CBV's for Create, Update, Delete Destination
    path('destinations/create/', views.DestinationCreate.as_view(), name='destination_create'),
    path('destinations/<int:pk>/update', views.DestinationUpdate.as_view(), name='destination_update'),
    path('destinations/<int:pk>/delete', views.DestinationDelete.as_view(), name='destination_delete'),
    path('destinations/<int:pk>', views.DestinationDetail.as_view(), name='destination_detail'),

    path('bookings/create/', views.BookingCreate.as_view(), name='booking_create'),
    path('bookings/<int:pk>', views.BookingDetail.as_view(), name='booking_detail'),
    path('bookings/<int:pk>/delete', views.BookingDelete.as_view(), name='booking_delete'), #added booking delete
    
]