from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views




urlpatterns = [
    path('', views.Home.as_view(), name='home'),  
    path('about/', views.about, name='about'),
    path('accounts/', include('django.contrib.auth.urls')),  
    path('signup/', views.signup, name='signup'),


    # CBV's for Create, Update, Delete Package
    path('packages/create/', views.PackageCreate.as_view(), name='package_create'),
    path('packages/<int:pk>/update', views.PackageUpdate.as_view(), name='package_update'),
    path('packages/<int:pk>/delete', views.PackageDelete.as_view(), name='package_delete'),
    path('packages/<int:pk>/', views.PackageDetail.as_view(), name='package_detail'),
    # ... other paths ...
    # path('packages/', views.PackageList.as_view(), name='package_list'),

        # CBV's for Create, Update, Delete Destination
    path('destinations/create/', views.DestinationCreate.as_view(), name='destination_create'),
    path('destinations/<int:pk>/update', views.DestinationUpdate.as_view(), name='destination_update'),
    path('destinations/<int:pk>/delete', views.DestinationDelete.as_view(), name='destination_delete'),
    path('destinations/<int:pk>', views.DestinationDetail.as_view(), name='destination_detail'),

    path('bookings/create/<int:destination_id>/', views.BookingCreate.as_view(), name='booking_create'),
    path('bookings/<int:pk>/', views.BookingDetail.as_view(), name='booking_detail'),
    path('bookings/<int:pk>/delete/', views.BookingDelete.as_view(), name='booking_delete'),
    
]